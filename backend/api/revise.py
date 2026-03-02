"""POST /revise/{job_id} endpoint — image revision via the agent pipeline."""

import json
import logging
import os

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func

from agents.graph import run_revision_graph
from agents.state import CosualState
from api.security import require_api_key
from database.connection import async_session
from database.models import Job, ImageRevision, generate_uuid

logger = logging.getLogger("cosual")

router = APIRouter(dependencies=[Depends(require_api_key)])


class ReviseRequest(BaseModel):
    revision_instruction: str


class ReviseResponse(BaseModel):
    job_id: str
    status: str
    revision_number: int


@router.post("/revise/{job_id}", response_model=ReviseResponse, status_code=202)
async def revise_image(job_id: str, req: ReviseRequest, background_tasks: BackgroundTasks):
    """Request an image revision. Runs through prompt_agent → image_agent → caption_agent."""
    async with async_session() as session:
        job = await session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.output_type != "image":
            raise HTTPException(status_code=400, detail="Revisions are only supported for image jobs")
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Job must be completed before revising")

        # Get next revision number
        result = await session.execute(
            select(func.coalesce(func.max(ImageRevision.revision_number), 0)).where(
                ImageRevision.job_id == job_id
            )
        )
        max_revision = result.scalar()
        next_revision = max_revision + 1

        # Resolve the absolute path to the current output image
        base_output_url = job.output_url  # e.g. /files/images/uuid.png
        local_base = base_output_url.replace("/files/", "./storage/", 1)
        abs_image_path = os.path.abspath(local_base)

        # Capture the current generated_prompt so the prompt agent has context
        current_prompt = job.generated_prompt or ""
        style_config = json.loads(job.style_config) if job.style_config else {}

        # Set job status to processing
        job.status = "processing"

        # Create revision record (output_url will be filled by the pipeline)
        revision = ImageRevision(
            id=generate_uuid(),
            job_id=job_id,
            revision_number=next_revision,
            revision_prompt=req.revision_instruction,
            output_url=None,
        )
        session.add(revision)
        await session.commit()

    logger.info("[revise] 📋 Revision %d queued for job %s → running through pipeline", next_revision, job_id)

    # Build the revision state and run through the agent pipeline
    revision_state: CosualState = {
        "job_id": job_id,
        "free_text": "",
        "github_url": None,
        "raw_code": None,
        "style_config": style_config,
        "architecture_summary": None,
        "generated_prompt": current_prompt,      # original prompt for context
        "output_url": None,
        "caption": None,
        "error": None,
        # Revision-specific fields
        "is_revision": True,
        "revision_instruction": req.revision_instruction,
        "base_image_path": abs_image_path,
        "revision_number": next_revision,
    }

    background_tasks.add_task(run_revision_graph, revision_state)

    return ReviseResponse(job_id=job_id, status="processing", revision_number=next_revision)
