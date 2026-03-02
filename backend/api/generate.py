"""POST /generate and GET /status/{job_id} endpoints."""

import json
import logging
from typing import Optional, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, model_validator

from agents.graph import run_graph
from agents.state import CosualState
from api.security import require_api_key
from database.connection import async_session
from database.models import Job, generate_uuid
from utils.title_generator import generate_title

logger = logging.getLogger("cosual")

router = APIRouter(dependencies=[Depends(require_api_key)])


class GenerateRequest(BaseModel):
    free_text: Optional[str] = None
    github_url: Optional[str] = None
    raw_code: Optional[str] = None
    output_type: Literal["image", "video"] = "image"
    duration: Optional[Literal[5, 10, 15]] = None
    aspect_ratio: Literal["16:9", "4:3", "1:1", "3:4", "9:16"] = "16:9"
    style: str = ""
    platform: Literal["linkedin", "instagram", "tiktok"] = "linkedin"

    @model_validator(mode="after")
    def validate_inputs(self):
        if self.github_url and self.raw_code:
            raise ValueError("github_url and raw_code are mutually exclusive")
        if not self.free_text and not self.github_url and not self.raw_code:
            raise ValueError("At least one of free_text, github_url, or raw_code is required")
        if self.output_type == "video" and self.duration is None:
            raise ValueError("duration is required when output_type is video")
        # Default free_text to empty string so downstream code doesn't break
        if self.free_text is None:
            self.free_text = ""
        return self


class GenerateResponse(BaseModel):
    job_id: str
    title: str
    status: str


class StatusResponse(BaseModel):
    job_id: str
    title: str
    status: str
    output_type: str
    output_url: Optional[str] = None
    caption: Optional[str] = None
    generated_prompt: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    """Start a new generation job."""
    job_id = generate_uuid()
    logger.info("[api] 📥 POST /generate — job_id=%s, output_type=%s", job_id, req.output_type)

    # Generate title immediately via LLM
    title = await generate_title(
        free_text=req.free_text,
        github_url=req.github_url,
        output_type=req.output_type,
        style=req.style,
    )

    # Build style config
    style_config = {
        "output_type": req.output_type,
        "aspect_ratio": req.aspect_ratio,
        "style": req.style,
        "platform": req.platform,
    }
    if req.duration is not None:
        style_config["duration"] = req.duration

    # Insert job into DB
    async with async_session() as session:
        job = Job(
            id=job_id,
            title=title,
            status="pending",
            output_type=req.output_type,
            user_input_text=req.free_text,
            user_input_github=req.github_url,
            user_input_code=req.raw_code,
            style_config=json.dumps(style_config),
        )
        session.add(job)
        await session.commit()

    # Build initial graph state
    initial_state: CosualState = {
        "job_id": job_id,
        "free_text": req.free_text,
        "github_url": req.github_url,
        "raw_code": req.raw_code,
        "style_config": style_config,
        "architecture_summary": None,
        "generated_prompt": None,
        "output_url": None,
        "caption": None,
        "error": None,
        # Not a revision
        "is_revision": False,
        "revision_instruction": None,
        "base_image_path": None,
        "revision_number": None,
    }

    # Kick off the graph in the background
    background_tasks.add_task(run_graph, initial_state)

    logger.info("[api] ✅ Job %s queued — title: %s", job_id, title)
    return GenerateResponse(job_id=job_id, title=title, status="pending")


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """Poll for job status."""
    async with async_session() as session:
        job = await session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return StatusResponse(
            job_id=job.id,
            title=job.title,
            status=job.status,
            output_type=job.output_type,
            output_url=job.output_url,
            caption=job.caption,
            generated_prompt=job.generated_prompt,
            error_message=job.error_message,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )
