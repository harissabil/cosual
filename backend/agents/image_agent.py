"""Text-to-Image Agent — generates images using qwen-image-max via MultiModalConversation SDK."""

import asyncio
import logging
import os
from functools import partial

import dashscope
from dashscope import MultiModalConversation
from dotenv import load_dotenv

from agents.state import CosualState
from database.connection import async_session
from database.models import ImageRevision, generate_uuid
from utils.file_storage import download_and_save, IMAGES_DIR

load_dotenv()

dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

logger = logging.getLogger("cosual")

ASPECT_RATIO_MAP = {
    "16:9": "1664*928",
    "4:3": "1280*960",
    "1:1": "1024*1024",
    "3:4": "960*1280",
    "9:16": "928*1664",
}


async def image_agent_node(state: CosualState) -> CosualState:
    """Generate or revise an image. Uses qwen-image-max for new, qwen-image-edit-max for revisions."""
    style_config = state.get("style_config", {})
    aspect_ratio = style_config.get("aspect_ratio", "16:9")
    size = ASPECT_RATIO_MAP.get(aspect_ratio, "1024*1024")
    job_id = state["job_id"]
    prompt = state["generated_prompt"]
    is_revision = state.get("is_revision", False)

    if is_revision:
        # ── Revision mode: call qwen-image-edit-max with base image ───────
        base_image_path = state.get("base_image_path", "")
        revision_number = state.get("revision_number", 2)

        logger.info("[image_agent] 🔄 REVISION mode — editing image (job=%s, rev=%d)", job_id, revision_number)
        logger.info("[image_agent]   base image: %s", base_image_path)
        logger.debug("[image_agent]   edit prompt: %.200s...", prompt)

        if not os.path.exists(base_image_path):
            raise FileNotFoundError(f"Base image not found at: {base_image_path}")

        messages = [
            {
                "role": "user",
                "content": [
                    {"image": base_image_path},
                    {"text": prompt},
                ],
            }
        ]

        rsp = await asyncio.to_thread(
            partial(
                MultiModalConversation.call,
                api_key=API_KEY,
                model="qwen-image-edit-max",
                messages=messages,
                stream=False,
                n=1,
                watermark=False,
                negative_prompt=" ",
                prompt_extend=True,
            )
        )

        if rsp.status_code != 200:
            logger.error("[image_agent] ❌ Image edit failed: status=%s, code=%s, message=%s",
                          rsp.status_code, rsp.code, rsp.message)
            raise RuntimeError(
                f"Image edit failed: status={rsp.status_code}, "
                f"code={rsp.code}, message={rsp.message}"
            )

        # Response: output.choices[0].message.content = [{"image": "url"}, ...]
        choices = rsp.output.choices
        if not choices:
            raise RuntimeError(f"Image edit returned no choices: {rsp.output}")

        content_list = choices[0].message.content
        logger.info("[image_agent] 📦 Edit response content: %s", content_list)

        image_url = None
        if isinstance(content_list, list):
            for item in content_list:
                if isinstance(item, dict) and "image" in item:
                    image_url = item["image"]
                    break

        if not image_url:
            raise RuntimeError(f"Could not extract image URL from edit response: {content_list}")

        logger.info("[image_agent] 🖼️ Revised image generated, downloading...")
        filename = f"{job_id}_rev{revision_number}.png"
        local_path = str(IMAGES_DIR / filename)
        await download_and_save(image_url, local_path)
        output_url = f"/files/images/{filename}"
        logger.info("[image_agent] 💾 Revised image saved to %s", output_url)
        logger.info("[image_agent] ✅ Image revision complete for job %s", job_id)
        return {**state, "output_url": output_url}

    # ── New generation mode: call qwen-image-max ──────────────────────────
    logger.info("[image_agent] 🚀 Generating image via qwen-image-max (size=%s, job=%s)", size, job_id)
    logger.debug("[image_agent] Prompt: %.200s...", prompt)

    messages = [
        {
            "role": "user",
            "content": [
                {"text": prompt}
            ],
        }
    ]

    rsp = await asyncio.to_thread(
        partial(
            MultiModalConversation.call,
            api_key=API_KEY,
            model="qwen-image-max",
            messages=messages,
            result_format="message",
            stream=False,
            watermark=False,
            prompt_extend=True,
            negative_prompt="low resolution, low quality, deformed limbs, deformed fingers, oversaturated, waxy, no facial details, overly smooth, AI-like, chaotic composition, blurry text, distorted text.",
            size=size,
        )
    )

    if rsp.status_code != 200:
        logger.error("[image_agent] ❌ Image generation failed: status=%s, code=%s, message=%s",
                      rsp.status_code, rsp.code, rsp.message)
        raise RuntimeError(
            f"Image generation failed: status={rsp.status_code}, "
            f"code={rsp.code}, message={rsp.message}"
        )

    # Response: output.choices[0].message.content = [{"image": "url"}, ...]
    choices = rsp.output.choices
    if not choices:
        logger.error("[image_agent] ❌ No choices in response: %s", rsp.output)
        raise RuntimeError("Image generation returned no choices")

    content_list = choices[0].message.content
    logger.info("[image_agent] 📦 Response content: %s", content_list)

    image_url = None
    if isinstance(content_list, list):
        for item in content_list:
            if isinstance(item, dict) and "image" in item:
                image_url = item["image"]
                break

    if not image_url:
        raise RuntimeError(f"Could not extract image URL from response: {content_list}")

    logger.info("[image_agent] 🖼️ Image generated, downloading from dashscope...")
    local_path = str(IMAGES_DIR / f"{job_id}.png")
    await download_and_save(image_url, local_path)
    output_url = f"/files/images/{job_id}.png"
    logger.info("[image_agent] 💾 Image saved to %s", output_url)

    # Insert first revision record (caption + generated_prompt filled later by run_graph)
    async with async_session() as session:
        revision = ImageRevision(
            id=generate_uuid(),
            job_id=job_id,
            revision_number=1,
            revision_prompt="original",
            output_url=output_url,
        )
        session.add(revision)
        await session.commit()

    logger.info("[image_agent] ✅ Image generation complete for job %s", job_id)
    return {**state, "output_url": output_url}
