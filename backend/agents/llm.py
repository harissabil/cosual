"""Shared Qwen LLM helper used by all agents."""

import asyncio
import logging
import os
from functools import partial

import dashscope
from dashscope import Generation
from dotenv import load_dotenv

load_dotenv()

dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

logger = logging.getLogger("cosual")

# ── Cosual system prompts per agent role ──────────────────────────────────────

COSUAL_SYSTEM_BASE = (
    "You are Cosual, an AI-powered content generation engine that transforms software "
    "concepts — free text descriptions, GitHub repositories, or raw code — into stunning "
    "visual content (architecture diagrams, video trailers of data pipelines) "
    "with captions tailored for social media platforms."
)

SYSTEM_PROMPTS = {
    "title_generator": (
        f"{COSUAL_SYSTEM_BASE}\n\n"
        "Your current role: TITLE GENERATOR.\n"
        "You create short, descriptive titles (5–8 words) that summarize what visual "
        "content will be created for the user. Output ONLY the title — no quotes, no "
        "explanation, no punctuation beyond what the title needs."
    ),
    "github_agent": (
        f"{COSUAL_SYSTEM_BASE}\n\n"
        "Your current role: GITHUB ANALYZER.\n"
        "You analyze GitHub repositories to extract architecture, data-flow, and system "
        "design information. Your output will be used downstream to generate visual art, "
        "so focus on structural clarity: components, data pipelines, layers, and how they "
        "connect. Be concise and precise."
    ),
    "code_analyzer": (
        f"{COSUAL_SYSTEM_BASE}\n\n"
        "Your current role: CODE ANALYZER.\n"
        "You analyze raw source code to extract a concise architecture summary covering: "
        "(1) what the code does, (2) its architecture or data flow, and (3) key components. "
        "Format the summary as a clear, structured paragraph suitable for generating "
        "visual art from."
    ),
    "prompt_agent": (
        f"{COSUAL_SYSTEM_BASE}\n\n"
        "Your current role: VISUAL PROMPT DESIGNER.\n"
        "You translate software architecture summaries into rich, detailed prompts "
        "optimized for AI image or video generation models. For images, describe "
        "composition, color palette, mood, lighting, and visual metaphors in a single "
        "dense paragraph. For videos, create shot-by-shot storyboards with precise "
        "timing, camera angles, and transitions."
    ),
    "caption_agent": (
        f"{COSUAL_SYSTEM_BASE}\n\n"
        "Your current role: SOCIAL MEDIA CAPTION WRITER.\n"
        "You write compelling social media captions for the visual content that Cosual "
        "generates. Match the tone and format to the target platform. Output ONLY the "
        "caption text — no preamble, no explanation."
    ),
}


async def call_qwen(prompt: str, system: str | None = None, agent_name: str = "unknown") -> str:
    """Call Qwen-plus and return the text response (non-blocking).

    Args:
        prompt: The user prompt to send.
        system: Override system prompt. If None, uses the agent-specific Cosual prompt.
        agent_name: Name of the calling agent (for logging and prompt lookup).
    """
    if system is None:
        system = SYSTEM_PROMPTS.get(agent_name, COSUAL_SYSTEM_BASE)

    logger.info("[%s] 🧠 Calling Qwen LLM (prompt length: %d chars)", agent_name, len(prompt))
    logger.debug("[%s] Prompt: %.200s...", agent_name, prompt)

    response = await asyncio.to_thread(
        partial(
            Generation.call,
            api_key=API_KEY,
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
    )
    if response.status_code != 200:
        logger.error("[%s] ❌ Qwen call failed: status=%s, code=%s, message=%s",
                      agent_name, response.status_code, response.code, response.message)
        raise RuntimeError(
            f"Qwen call failed: status={response.status_code}, "
            f"code={response.code}, message={response.message}"
        )
    # dashscope may return text in output.text or output.choices
    if response.output.text:
        result = response.output.text
    elif response.output.choices:
        result = response.output.choices[0].message.content
    else:
        logger.error("[%s] ❌ Qwen returned empty output", agent_name)
        raise RuntimeError("Qwen returned empty output")

    logger.info("[%s] ✅ Qwen response received (%d chars)", agent_name, len(result))
    logger.debug("[%s] Response: %.200s...", agent_name, result)
    return result
