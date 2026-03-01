"""LangGraph graph definition — main orchestrator for the Cosual pipeline."""

import logging
import traceback

from langgraph.graph import StateGraph, END

from agents.state import CosualState
from agents.router import input_router_node, route_input
from agents.github_agent import github_agent_node
from agents.code_analyzer import code_analyzer_node
from agents.prompt_agent import prompt_agent_node
from agents.image_agent import image_agent_node
from agents.video_agent import video_agent_node
from agents.caption_agent import caption_agent_node

from database.connection import async_session
from database.models import Job

logger = logging.getLogger("cosual")


def _route_output_type(state: CosualState) -> str:
    """Route to image or video agent based on output_type."""
    output_type = state.get("style_config", {}).get("output_type", "image")
    if output_type == "video":
        logger.info("[graph] 🔀 Routing to → video_agent")
        return "video_agent"
    logger.info("[graph] 🔀 Routing to → image_agent")
    return "image_agent"


def build_graph() -> StateGraph:
    """Build and compile the Cosual LangGraph state graph."""
    graph = StateGraph(CosualState)

    # Add nodes
    graph.add_node("input_router", input_router_node)
    graph.add_node("github_agent", github_agent_node)
    graph.add_node("code_analyzer", code_analyzer_node)
    graph.add_node("prompt_agent", prompt_agent_node)
    graph.add_node("image_agent", image_agent_node)
    graph.add_node("video_agent", video_agent_node)
    graph.add_node("caption_agent", caption_agent_node)

    # Set entry point
    graph.set_entry_point("input_router")

    # After input_router: conditional routing
    graph.add_conditional_edges(
        "input_router",
        route_input,
        {
            "github_agent": "github_agent",
            "code_analyzer": "code_analyzer",
            "prompt_agent": "prompt_agent",
        },
    )

    # After github/code agents → prompt_agent
    graph.add_edge("github_agent", "prompt_agent")
    graph.add_edge("code_analyzer", "prompt_agent")

    # After prompt_agent: conditional routing to image or video
    graph.add_conditional_edges(
        "prompt_agent",
        _route_output_type,
        {
            "image_agent": "image_agent",
            "video_agent": "video_agent",
        },
    )

    # After image/video → caption
    graph.add_edge("image_agent", "caption_agent")
    graph.add_edge("video_agent", "caption_agent")

    # After caption → END
    graph.add_edge("caption_agent", END)

    return graph.compile()


# Compiled graph instance
cosual_graph = build_graph()


async def run_graph(state: CosualState) -> None:
    """Run the full pipeline and update the job in the database."""
    job_id = state["job_id"]

    logger.info("=" * 60)
    logger.info("[graph] 🏁 STARTING PIPELINE for job %s", job_id)
    logger.info("[graph]   free_text: %.80s...", state.get("free_text", ""))
    logger.info("[graph]   github_url: %s", state.get("github_url"))
    logger.info("[graph]   raw_code: %s", "yes" if state.get("raw_code") else "no")
    logger.info("[graph]   output_type: %s", state.get("style_config", {}).get("output_type"))
    logger.info("=" * 60)

    try:
        # Set status to processing
        async with async_session() as session:
            job = await session.get(Job, job_id)
            if job:
                job.status = "processing"
                await session.commit()
        logger.info("[graph] 📋 Job status → processing")

        # Run the graph
        result = await cosual_graph.ainvoke(state)

        # Update job with results
        async with async_session() as session:
            job = await session.get(Job, job_id)
            if job:
                job.status = "completed"
                job.output_url = result.get("output_url")
                job.caption = result.get("caption")
                job.generated_prompt = result.get("generated_prompt")
                await session.commit()

            # Also update the initial revision record with caption + prompt
            if result.get("output_url") and result.get("style_config", {}).get("output_type") == "image":
                from database.models import ImageRevision
                from sqlalchemy import select
                rev_result = await session.execute(
                    select(ImageRevision).where(
                        ImageRevision.job_id == job_id,
                        ImageRevision.revision_number == 1,
                    )
                )
                rev = rev_result.scalar_one_or_none()
                if rev:
                    rev.caption = result.get("caption")
                    rev.generated_prompt = result.get("generated_prompt")
                    await session.commit()

        logger.info("=" * 60)
        logger.info("[graph] 🎉 PIPELINE COMPLETED for job %s", job_id)
        logger.info("[graph]   output_url: %s", result.get("output_url"))
        logger.info("[graph]   caption length: %d chars", len(result.get("caption") or ""))
        logger.info("=" * 60)

    except Exception as e:
        logger.error("=" * 60)
        logger.error("[graph] 💥 PIPELINE FAILED for job %s", job_id)
        logger.error("[graph]   Error: %s", str(e))
        logger.error("[graph]   Traceback:\n%s", traceback.format_exc())
        logger.error("=" * 60)

        # On failure, mark the job as failed
        async with async_session() as session:
            job = await session.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                await session.commit()


async def run_revision_graph(state: CosualState) -> None:
    """Run the revision sub-flow: prompt_agent → image_agent → caption_agent.

    This reuses the same compiled graph but enters with is_revision=True,
    which causes the router to skip straight to prompt_agent, and prompt_agent
    + image_agent to use revision-specific logic.
    """
    job_id = state["job_id"]
    revision_number = state.get("revision_number", 0)

    logger.info("=" * 60)
    logger.info("[graph] 🔄 STARTING REVISION PIPELINE for job %s (rev %d)", job_id, revision_number)
    logger.info("[graph]   instruction: %s", state.get("revision_instruction"))
    logger.info("[graph]   base_image: %s", state.get("base_image_path"))
    logger.info("=" * 60)

    try:
        # Run prompt_agent → image_agent → caption_agent directly
        from agents.prompt_agent import prompt_agent_node
        from agents.image_agent import image_agent_node
        from agents.caption_agent import caption_agent_node

        logger.info("[graph] 📋 Step 1/3: Prompt Agent (revision mode)")
        state = await prompt_agent_node(state)

        logger.info("[graph] 📋 Step 2/3: Image Agent (revision mode)")
        state = await image_agent_node(state)

        logger.info("[graph] 📋 Step 3/3: Caption Agent")
        state = await caption_agent_node(state)

        # Update job + revision record in DB
        async with async_session() as session:
            from database.models import ImageRevision
            from sqlalchemy import select

            job = await session.get(Job, job_id)
            if job:
                job.status = "completed"
                job.output_url = state.get("output_url")
                job.caption = state.get("caption")
                job.generated_prompt = state.get("generated_prompt")

            # Update revision record with output_url, caption, and generated_prompt
            result = await session.execute(
                select(ImageRevision).where(
                    ImageRevision.job_id == job_id,
                    ImageRevision.revision_number == revision_number,
                )
            )
            revision = result.scalar_one_or_none()
            if revision:
                revision.output_url = state.get("output_url")
                revision.caption = state.get("caption")
                revision.generated_prompt = state.get("generated_prompt")

            await session.commit()

        logger.info("=" * 60)
        logger.info("[graph] 🎉 REVISION PIPELINE COMPLETED for job %s", job_id)
        logger.info("[graph]   output_url: %s", state.get("output_url"))
        logger.info("=" * 60)

    except Exception as e:
        logger.error("=" * 60)
        logger.error("[graph] 💥 REVISION PIPELINE FAILED for job %s", job_id)
        logger.error("[graph]   Error: %s", str(e))
        logger.error("[graph]   Traceback:\n%s", traceback.format_exc())
        logger.error("=" * 60)

        async with async_session() as session:
            job = await session.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                await session.commit()
