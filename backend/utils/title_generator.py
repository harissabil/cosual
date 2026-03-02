import asyncio
import logging
import os
from functools import partial
from typing import Optional

import dashscope
from dashscope import MultiModalConversation
from dotenv import load_dotenv

from agents.llm import SYSTEM_PROMPTS
from agents.models import LLM_FLASH_MODEL

load_dotenv()

dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

logger = logging.getLogger("cosual")


async def generate_title(
    free_text: str,
    github_url: Optional[str] = None,
    output_type: str = "image",
    style: str = "",
) -> str:
    """Generate a short descriptive title for a job using Qwen LLM."""
    prompt = (
        f'Given this user request for an AI-generated visual, create a short, '
        f'descriptive title (5-8 words max) that summarizes what will be created. '
        f'Output only the title, nothing else.\n\n'
        f'User request: "{free_text}"\n'
        f'GitHub URL: {github_url or "none"}\n'
        f'Output type: {output_type}\n'
        f'Style: {style}'
    )

    logger.info("[title_generator] 🚀 Generating title for new job")

    try:
        response = await asyncio.to_thread(
            partial(
                MultiModalConversation.call,
                api_key=API_KEY,
                model=LLM_FLASH_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS["title_generator"]},
                    {"role": "user", "content": prompt},
                ],
                enable_thinking=False,
            )
        )
        # dashscope MultiModalConversation returns content as a list of dicts
        # e.g. [{"text": "..."}] — extract the plain text string
        text = response.output.text
        if not text and response.output.choices:
            content = response.output.choices[0].message.content
            if isinstance(content, list):
                text_parts = [part.get("text", "") for part in content if isinstance(part, dict)]
                text = "".join(text_parts)
            elif isinstance(content, str):
                text = content
        if text:
            title = text.strip().strip('"')
            logger.info("[title_generator] ✅ Title generated: %s", title)
            return title
        logger.warning("[title_generator] ⚠️ Empty LLM response, using fallback")
        return " ".join(free_text.split()[:6])
    except Exception as e:
        logger.warning("[title_generator] ⚠️ LLM call failed (%s), using fallback title", e)
        words = free_text.split()[:6]
        return " ".join(words)
