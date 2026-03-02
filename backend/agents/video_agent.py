"""Text-to-Video Agent — generates videos using dashscope wan2.6-t2v."""

import asyncio
import logging
import os
from functools import partial

import dashscope
from dashscope import VideoSynthesis
from dotenv import load_dotenv

from agents.state import CosualState
from agents.models import VIDEO_MODEL
from utils.file_storage import download_and_save, VIDEOS_DIR

load_dotenv()

dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

logger = logging.getLogger("cosual")

VIDEO_SIZE_MAP = {
    "16:9": "1280*720",
    "4:3": "960*720",
    "1:1": "720*720",
    "3:4": "720*960",
    "9:16": "720*1280",
}


async def video_agent_node(state: CosualState) -> CosualState:
    """Generate a video from the generated prompt and save locally."""
    style_config = state.get("style_config", {})
    aspect_ratio = style_config.get("aspect_ratio", "16:9")
    duration = style_config.get("duration", 5)
    size = VIDEO_SIZE_MAP.get(aspect_ratio, "1280*720")
    job_id = state["job_id"]
    prompt = state["generated_prompt"]

    logger.info("[video_agent] 🚀 Generating video (size=%s, duration=%ss, job=%s)", size, duration, job_id)
    logger.debug("[video_agent] Prompt: %.200s...", prompt)

    rsp = await asyncio.to_thread(
        partial(
            VideoSynthesis.async_call,
            api_key=API_KEY,
            model=VIDEO_MODEL,
            prompt=prompt,
            size=size,
            shot_type="multi",
            duration=duration,
            prompt_extend=True,
            watermark=False,
            negative_prompt="",
        )
    )

    if rsp.status_code != 200:
        logger.error("[video_agent] ❌ Video async_call failed: status=%s, code=%s, message=%s",
                      rsp.status_code, rsp.code, rsp.message)
        raise RuntimeError(
            f"Video generation async_call failed: status={rsp.status_code}, "
            f"code={rsp.code}, message={rsp.message}"
        )

    logger.info("[video_agent] ⏳ Video task submitted, polling for completion...")

    # Poll until complete (run in thread to avoid blocking event loop)
    rsp = await asyncio.to_thread(
        partial(VideoSynthesis.wait, task=rsp, api_key=API_KEY)
    )

    if rsp.status_code != 200:
        logger.error("[video_agent] ❌ Video generation failed: status=%s, code=%s, message=%s",
                      rsp.status_code, rsp.code, rsp.message)
        raise RuntimeError(
            f"Video generation failed: status={rsp.status_code}, "
            f"code={rsp.code}, message={rsp.message}"
        )

    video_url = rsp.output.video_url
    logger.info("[video_agent] 🎬 Video generated, downloading from dashscope...")
    local_path = str(VIDEOS_DIR / f"{job_id}.mp4")
    await download_and_save(video_url, local_path)
    output_url = f"/files/videos/{job_id}.mp4"

    logger.info("[video_agent] ✅ Video saved to %s", output_url)
    return {**state, "output_url": output_url}
