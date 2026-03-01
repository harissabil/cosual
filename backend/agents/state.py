"""Shared state TypedDict for the LangGraph agent graph."""

from typing import TypedDict, Optional


class CosualState(TypedDict):
    job_id: str
    free_text: str
    github_url: Optional[str]
    raw_code: Optional[str]
    style_config: dict
    architecture_summary: Optional[str]
    generated_prompt: Optional[str]
    output_url: Optional[str]
    caption: Optional[str]
    error: Optional[str]
    # Revision fields (set only during a revision run)
    is_revision: Optional[bool]
    revision_instruction: Optional[str]
    base_image_path: Optional[str]          # absolute local path to the base image
    revision_number: Optional[int]
