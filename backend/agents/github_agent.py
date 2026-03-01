"""GitHub Agent — 3-step progressive fallback to extract architecture info from a repo."""

import base64
import logging
import re
from typing import Optional

import httpx

from agents.llm import call_qwen
from agents.state import CosualState

logger = logging.getLogger("cosual")

GITHUB_API = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"


def parse_repo(url: str) -> tuple[str, str]:
    """Extract owner/repo from a GitHub URL."""
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not match:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return match.group(1), match.group(2)


async def _step1_readme(client: httpx.AsyncClient, owner: str, repo: str) -> Optional[str]:
    """Step 1: Read the README and ask LLM to extract architecture info."""
    logger.info("[github_agent] 📖 Step 1: Reading README for %s/%s", owner, repo)
    resp = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}/readme")
    if resp.status_code in (403, 429):
        logger.warning("[github_agent] ⚠️ GitHub rate limited (status %d), skipping README", resp.status_code)
        return None
    if resp.status_code != 200:
        logger.warning("[github_agent] ⚠️ README not found (status %d)", resp.status_code)
        return None

    content_b64 = resp.json().get("content", "")
    try:
        readme_text = base64.b64decode(content_b64).decode("utf-8", errors="replace")
    except Exception:
        logger.warning("[github_agent] ⚠️ Failed to decode README content")
        return None

    logger.info("[github_agent] 📖 README fetched (%d chars), analyzing with LLM...", len(readme_text))
    prompt = (
        "Read this README. If it contains clear information about the architecture, "
        "data flow, or system design of this project, extract and summarize it concisely. "
        "If not, reply with exactly: UNCLEAR\n\n"
        f"{readme_text[:8000]}"
    )
    result = await call_qwen(prompt, agent_name="github_agent")
    if result.strip() == "UNCLEAR":
        logger.info("[github_agent] 📖 Step 1 result: UNCLEAR — moving to Step 2")
        return None
    logger.info("[github_agent] ✅ Step 1 success — architecture extracted from README")
    return result.strip()


async def _step2_file_tree(client: httpx.AsyncClient, owner: str, repo: str) -> tuple[Optional[str], list[str]]:
    """Step 2: Read the file tree and ask LLM to infer architecture."""
    logger.info("[github_agent] 🌳 Step 2: Reading file tree for %s/%s", owner, repo)
    resp = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1")
    if resp.status_code in (403, 429):
        logger.warning("[github_agent] ⚠️ GitHub rate limited (status %d), skipping file tree", resp.status_code)
        return None, []
    if resp.status_code != 200:
        logger.warning("[github_agent] ⚠️ File tree not found (status %d)", resp.status_code)
        return None, []

    tree = resp.json().get("tree", [])
    file_paths = [item["path"] for item in tree if item.get("type") == "blob"]
    logger.info("[github_agent] 🌳 File tree fetched (%d files), analyzing with LLM...", len(file_paths))

    prompt = (
        "Here is the file tree of a software project. Based on the file and folder names, "
        "describe the likely architecture and data flow of the project. "
        "If the tree gives no meaningful signal, reply with exactly: UNCLEAR\n\n"
        + "\n".join(file_paths[:500])
    )
    result = await call_qwen(prompt, agent_name="github_agent")
    if result.strip() == "UNCLEAR":
        logger.info("[github_agent] 🌳 Step 2 result: UNCLEAR — moving to Step 3")
        return None, file_paths
    logger.info("[github_agent] ✅ Step 2 success — architecture inferred from file tree")
    return result.strip(), file_paths


async def _step3_key_files(
    client: httpx.AsyncClient, owner: str, repo: str, file_paths: list[str]
) -> str:
    """Step 3: Let the LLM pick which files to read, then extract architecture info."""
    logger.info("[github_agent] 📄 Step 3: Asking LLM to select key files for %s/%s", owner, repo)

    # Ask the LLM which files are most architecturally relevant
    file_list = "\n".join(file_paths[:800])
    selection_prompt = (
        "Here is the complete file tree of a software project (any language/framework).\n\n"
        f"{file_list}\n\n"
        "Select up to 5 files that are MOST likely to reveal the project's architecture, "
        "data flow, or system design. Consider files like:\n"
        "- Entry points (main, app, index, server, etc.)\n"
        "- Configuration files (docker-compose, Makefile, build configs, CI/CD)\n"
        "- Files with names suggesting architecture (pipeline, workflow, dag, graph, router, etc.)\n"
        "- Core module files in any language (Python, Java, Go, JS/TS, Rust, etc.)\n\n"
        "Output ONLY the exact file paths, one per line. No explanations, no numbering, "
        "no extra text. Just the paths."
    )

    selection_result = await call_qwen(selection_prompt, agent_name="github_agent")
    selected_files = [
        line.strip().strip("`").strip("-").strip()
        for line in selection_result.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Validate that the selected files actually exist in the tree
    file_set = set(file_paths)
    valid_files = [fp for fp in selected_files if fp in file_set][:5]

    if not valid_files:
        # Fallback: grab first 5 source files from the tree
        logger.warning("[github_agent] ⚠️ LLM selected no valid files, using fallback")
        source_exts = (".py", ".java", ".go", ".ts", ".js", ".rs", ".rb", ".kt", ".cs", ".cpp", ".c")
        valid_files = [fp for fp in file_paths if any(fp.endswith(ext) for ext in source_exts)][:5]

    logger.info("[github_agent] 📄 LLM selected %d files to read: %s", len(valid_files), valid_files)

    # Fetch the selected files
    parts: list[str] = []
    for fp in valid_files:
        resp = await client.get(f"{RAW_BASE}/{owner}/{repo}/HEAD/{fp}")
        if resp.status_code == 200:
            content = resp.text[:3000]
            parts.append(f"=== {fp} ===\n{content}")
        else:
            logger.warning("[github_agent] ⚠️ Failed to fetch %s (status %d)", fp, resp.status_code)

    if not parts:
        return f"GitHub repository {owner}/{repo} — could not read any source files."

    combined = "\n\n".join(parts)
    prompt = (
        "Here are key files from a software project, selected because they are most likely "
        "to reveal the architecture. Extract a clear summary of the architecture, data pipeline, "
        "or system flow. Be concise.\n\n"
        f"{combined}"
    )
    result = (await call_qwen(prompt, agent_name="github_agent")).strip()
    logger.info("[github_agent] ✅ Step 3 complete — summary extracted from LLM-selected files")
    return result


async def github_agent_node(state: CosualState) -> CosualState:
    """GitHub Agent: 3-step fallback to extract architecture summary."""
    url = state["github_url"]
    if not url:
        return state

    logger.info("[github_agent] 🚀 Starting GitHub analysis for: %s", url)
    try:
        owner, repo = parse_repo(url)
    except ValueError as e:
        logger.error("[github_agent] ❌ Invalid GitHub URL: %s", e)
        return {**state, "error": str(e)}

    async with httpx.AsyncClient(timeout=30) as client:
        summary = await _step1_readme(client, owner, repo)
        if summary:
            return {**state, "architecture_summary": summary}

        summary, file_paths = await _step2_file_tree(client, owner, repo)
        if summary:
            return {**state, "architecture_summary": summary}

        if file_paths:
            summary = await _step3_key_files(client, owner, repo, file_paths)
            return {**state, "architecture_summary": summary}

    logger.warning("[github_agent] ⚠️ All steps exhausted, using fallback summary")
    return {**state, "architecture_summary": f"GitHub repository: {owner}/{repo}"}
