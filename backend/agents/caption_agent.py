"""Caption Agent — generates social media captions with full context."""

import logging

from agents.llm import call_qwen
from agents.state import CosualState

logger = logging.getLogger("cosual")

LINKEDIN_RULES = """
- Tone: authoritative, insightful, professional — like a senior engineer sharing a discovery
- Length: 3–5 sentences (hook → insight → call to action)
- Structure: Start with a bold single-line hook (no "I" subject), then 2-3 lines of insight, end with a question or CTA
- Hashtags: 3–5 highly relevant tech hashtags at the very end (e.g. #DataEngineering #MLOps #SystemDesign)
- NO emojis, NO exclamation spam, NO "Excited to share" openers
- Example hook style: "Most data pipelines fail silently. Here's what a Medallion Architecture actually looks like."
"""

INSTAGRAM_RULES = """
- Tone: energetic, visual-first, exciting — like a tech creator showing off something cool
- Length: 2–3 punchy sentences max (scroll-stopping hook → wow moment → CTA)
- Structure: First sentence must stop the scroll. Second sentence explains or amazes. Third invites engagement.
- Hashtags: 8–12 hashtags after a line break — mix popular (#AI #Tech) and niche (#DataPipeline #MLVisualized)
- Emojis: 2–4 emojis, used purposefully (not randomly sprinkled)
- Example style: "Your data pipeline, but make it cinematic. 🎬 This is what Medallion Architecture actually looks like under the hood. Drop a 🔥 if you want the breakdown."
"""


async def caption_agent_node(state: CosualState) -> CosualState:
    """Generate a platform-appropriate caption with full context."""
    style_config = state.get("style_config", {})
    platform = style_config.get("platform", "linkedin")
    style = style_config.get("style", "modern")
    output_type = style_config.get("output_type", "image")
    free_text = state.get("free_text", "")
    architecture_summary = state.get("architecture_summary", "")
    generated_prompt = state.get("generated_prompt", "")

    platform_rules = LINKEDIN_RULES if platform == "linkedin" else INSTAGRAM_RULES
    media_type = "image" if output_type == "image" else "video"

    # Build the richest possible context for the caption
    context_parts = []
    if free_text:
        context_parts.append(f"User's original concept: {free_text}")
    if architecture_summary:
        context_parts.append(f"Technical summary: {architecture_summary[:500]}")
    if generated_prompt:
        context_parts.append(f"Visual description of the generated {media_type}: {generated_prompt[:600]}")
    context = "\n\n".join(context_parts)

    logger.info("[caption_agent] 🚀 Generating %s caption for %s", media_type, platform)

    prompt = f"""You are a world-class social media copywriter specializing in tech content.

## Context
{context}

Visual style: {style}
Content type: AI-generated {media_type}
Platform: {platform.upper()}

## Platform Rules
{platform_rules}

## Your Task
Write ONE caption for this {media_type} following the platform rules exactly.
The caption should make someone stop scrolling and feel like they MUST engage.
Do NOT mention "AI-generated" or "Cosual" — present it as a real visual insight.

Output ONLY the caption. No preamble, no labels, no explanation."""

    caption = await call_qwen(prompt, agent_name="caption_agent")
    logger.info("[caption_agent] ✅ Caption generated (%d chars)", len(caption))
    return {**state, "caption": caption.strip()}
