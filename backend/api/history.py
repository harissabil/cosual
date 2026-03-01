"""GET /history and GET /history/{job_id} endpoints."""

import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.connection import async_session
from database.models import Job

router = APIRouter()


class HistoryItem(BaseModel):
    job_id: str
    title: str
    status: str
    output_type: str
    output_url: Optional[str] = None
    created_at: str


class HistoryListResponse(BaseModel):
    items: list[HistoryItem]
    total: int


class UserInput(BaseModel):
    free_text: str
    github_url: Optional[str] = None
    raw_code: Optional[str] = None


class RevisionItem(BaseModel):
    revision_number: int
    revision_prompt: str
    output_url: Optional[str] = None
    caption: Optional[str] = None
    generated_prompt: Optional[str] = None
    created_at: str


class HistoryDetailResponse(BaseModel):
    job_id: str
    title: str
    status: str
    output_type: str
    output_url: Optional[str] = None
    caption: Optional[str] = None
    generated_prompt: Optional[str] = None
    user_input: UserInput
    style_config: Optional[dict] = None
    revisions: list[RevisionItem] = []
    created_at: str
    updated_at: str


@router.get("/history", response_model=HistoryListResponse)
async def list_history():
    """Return all jobs, most recent first."""
    async with async_session() as session:
        result = await session.execute(
            select(Job).order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()

        items = [
            HistoryItem(
                job_id=j.id,
                title=j.title,
                status=j.status,
                output_type=j.output_type,
                output_url=j.output_url,
                created_at=j.created_at.isoformat(),
            )
            for j in jobs
        ]
        return HistoryListResponse(items=items, total=len(items))


@router.get("/history/{job_id}", response_model=HistoryDetailResponse)
async def get_history_detail(job_id: str):
    """Return full details of one job including revision history."""
    async with async_session() as session:
        result = await session.execute(
            select(Job)
            .where(Job.id == job_id)
            .options(selectinload(Job.revisions))
        )
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Parse style_config JSON
        style_config = None
        if job.style_config:
            try:
                style_config = json.loads(job.style_config)
            except json.JSONDecodeError:
                style_config = None

        revisions = [
            RevisionItem(
                revision_number=r.revision_number,
                revision_prompt=r.revision_prompt,
                output_url=r.output_url,
                caption=r.caption,
                generated_prompt=r.generated_prompt,
                created_at=r.created_at.isoformat(),
            )
            for r in job.revisions
        ]

        return HistoryDetailResponse(
            job_id=job.id,
            title=job.title,
            status=job.status,
            output_type=job.output_type,
            output_url=job.output_url,
            caption=job.caption,
            generated_prompt=job.generated_prompt,
            user_input=UserInput(
                free_text=job.user_input_text,
                github_url=job.user_input_github,
                raw_code=job.user_input_code,
            ),
            style_config=style_config,
            revisions=revisions,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )
