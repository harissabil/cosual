"""Code Analyzer Agent — analyzes raw code to produce an architecture summary."""

import logging

from agents.llm import call_qwen
from agents.state import CosualState

logger = logging.getLogger("cosual")


async def code_analyzer_node(state: CosualState) -> CosualState:
    """Analyze raw code and produce a structured architecture summary."""
    raw_code = state.get("raw_code", "")
    if not raw_code:
        return state

    logger.info("[code_analyzer] 🚀 Analyzing raw code (%d chars)", len(raw_code))

    prompt = (
        "You are a software architect. Analyze the following code and produce a concise "
        "summary of: (1) what it does, (2) its architecture or data flow, (3) the key "
        "components or modules involved. Format it as a clear, structured paragraph "
        "suitable for generating visual art from.\n\n"
        f"{raw_code[:8000]}"
    )

    summary = await call_qwen(prompt, agent_name="code_analyzer", enable_thinking=True)
    logger.info("[code_analyzer] ✅ Code analysis complete")
    return {**state, "architecture_summary": summary.strip()}
