"""Prompt Agent — builds image/video prompts. Diagram-first, LLM only for creative styles."""

import logging

from agents.llm import call_qwen
from agents.state import CosualState

logger = logging.getLogger("cosual")

STYLE_OVERRIDE_MAP = {
    "hollywood": (
        "cinematic blockbuster aesthetic, dramatic volumetric lighting, rich color grading "
        "(deep teals and warm oranges), lens flare, photorealistic, epic wide-angle shots"
    ),
    "neon cyberpunk": (
        "cyberpunk noir, neon magenta and cyan glow on dark background, glitch effects, "
        "holographic UI overlays, high contrast synthwave color palette"
    ),
    "vintage retro": (
        "vintage retro illustration, muted warm palette, halftone textures, hand-drawn "
        "linework, aged paper feel, 1970s tech poster aesthetic"
    ),
    "data viz futuristic": (
        "futuristic data visualization, glowing network graphs on dark background, "
        "particle systems, luminous data streams, sci-fi holographic HUD elements"
    ),
    "minimalist clean": (
        "ultra-minimalist flat vector, soft pastel palette, generous white space, "
        "thin clean lines, simple geometric shapes"
    ),
    "architectural classic": (
        "classic technical blueprint, isometric 3D diagram, monochrome base with blue "
        "accent lines, engineering drawing aesthetic, sharp geometric nodes and arrows"
    ),
}

ASPECT_RATIO_COMPOSITION = {
    "16:9": "wide landscape, horizontal left-to-right flow",
    "4:3":  "balanced layout, grid or top-to-bottom layered flow",
    "1:1":  "centered square, radial or stacked layout",
    "3:4":  "portrait, top-to-bottom vertical flow",
    "9:16": "vertical portrait, top-to-bottom flow, mobile-optimized",
}


def _resolve_style(style: str) -> tuple[str | None, bool]:
    """
    Returns (style_description, is_creative).
    is_creative=True only when user explicitly picks a named creative style.
    Returns (None, False) for default/blank/generic — use diagram prompt directly.
    """
    style_lower = style.lower().strip()
    for key, val in STYLE_OVERRIDE_MAP.items():
        if style_lower and (key in style_lower or style_lower in key):
            return val, True
    return None, False


async def _build_diagram_image_prompt(concept: str, aspect_ratio: str, platform: str) -> str:
    """
    Ask the LLM to extract real component names from the architecture summary,
    then inject them as explicit labels into a tightly constrained diagram prompt.
    """
    composition = ASPECT_RATIO_COMPOSITION.get(aspect_ratio, "balanced layout")
    platform_note = (
        "polished and professional, suitable for a technical LinkedIn audience"
        if platform == "linkedin"
        else "clean and clear, suitable for Instagram tech content"
    )

    components_raw = await call_qwen(
        f"""From this architecture summary, extract the most important components that should appear as labeled boxes in an architecture diagram.

{concept}

Rules:
- Output maximum 12 components (pick the most important ones)
- Group them by layer
- Output format — each line: LAYER: Name1, Name2, Name3
- Layer names: API, Service, Storage, External, Auth
- Component names must be short (1-3 words max), plain English only, no symbols, no hex codes, no slashes

Example output:
API: UserController, ListingController, MessageController
Service: UserService, ListingService, MessageService
Storage: CosmosDB, BlobStorage
Auth: JwtFilter

Output the grouped list only. No explanation, no extra text.""",
        agent_name="prompt_agent",
        enable_thinking=False,
    )

    # Parse "LAYER: Name1, Name2" format into two separate structures
    layer_color_map = {
        "api":      ("API layer",      "blue (#4A90D9)"),
        "service":  ("Service layer",  "purple (#7B68EE)"),
        "storage":  ("Storage layer",  "green (#5CB85C)"),
        "external": ("External layer", "orange (#F0A500)"),
        "auth":     ("Auth layer",     "red (#E05C5C)"),
    }

    layer_blocks = []
    label_only_list = []
    for line in components_raw.strip().splitlines():
        if ":" not in line:
            continue
        layer_part, _, names_part = line.partition(":")
        layer_key = layer_part.strip().lower()
        names = [n.strip() for n in names_part.split(",") if n.strip()]
        if not names:
            continue
        color_info = layer_color_map.get(layer_key, (layer_key.title() + " layer", "gray"))
        layer_blocks.append(f"{color_info[0]} ({color_info[1]}): {', '.join(names)}")
        label_only_list.extend(names)

    if not layer_blocks:
        layer_blocks = ["API layer (blue): ComponentA, ComponentB",
                        "Service layer (purple): ServiceA",
                        "Storage layer (green): Database"]
        label_only_list = ["ComponentA", "ComponentB", "ServiceA", "Database"]

    layers_description = "\n".join(f"  - {b}" for b in layer_blocks)
    all_labels = ", ".join(f'"{n}"' for n in label_only_list)

    return (
        f"A clean, professional software architecture diagram. {composition}. "
        f"Pure white background. "
        f"The diagram has boxes organized in horizontal rows by layer, top to bottom:\n"
        f"{layers_description}\n\n"
        f"Each box shows ONLY its component name as the label — nothing else inside the box. "
        f"The exact label text for every box must be one of: {all_labels}. "
        f"Box labels are written in plain English only. "
        f"Directional arrows connect boxes between layers to show data flow. "
        f"Font: clean dark sans-serif, large and sharp, fully legible. "
        f"NO hex codes, NO symbols, NO slashes, NO layer names inside boxes — only the component name. "
        f"NO 3D. NO gradients. NO illustrations. NO humans. NO cinematic effects. "
        f"Style: flat 2D diagram, identical to AWS or GCP official architecture diagrams. "
        f"{platform_note}. High resolution, sharp text."
    )


def _build_diagram_video_prompt(concept: str, aspect_ratio: str, duration: int, platform: str) -> str:
    """Build a deterministic storyboard for the default diagram/explainer video case."""
    composition = ASPECT_RATIO_COMPOSITION.get(aspect_ratio, "balanced layout")
    num_shots = {5: 3, 10: 4, 15: 5}.get(duration, 4)
    seconds_per_shot = duration // num_shots

    return (
        f"A professional animated architecture explainer video. {composition}. "
        f"White background, clean flat 2D diagram style similar to AWS re:Invent walkthrough videos. "
        f"No cinematic effects, no 3D, no dramatic lighting. "
        f"Concept being visualized: {concept[:600]}. "
        f"Storyboard ({num_shots} shots, {duration}s total):\n"
        + "\n".join([
            f"Shot {i+1} [{i*seconds_per_shot}–{(i+1)*seconds_per_shot}s]: "
            f"Static wide shot. A labeled component or layer of the architecture appears on screen "
            f"with a smooth fade-in, connected to adjacent components by animated arrows. "
            f"Text label visible. Neutral background. Transition: smooth dissolve."
            for i in range(num_shots)
        ])
        + "\nProfessional explainer video style. High resolution, sharp text labels."
    )


async def prompt_agent_node(state: CosualState) -> CosualState:
    """Generate image or video prompt. Default = deterministic diagram. Creative = LLM.
    In revision mode, generates an edit prompt for qwen-image-edit-max."""

    # ── Revision mode: build an edit prompt from the instruction ──────────
    if state.get("is_revision"):
        revision_instruction = state.get("revision_instruction", "")
        original_prompt = state.get("generated_prompt", "")

        logger.info("[prompt_agent] 🔄 REVISION MODE — building edit prompt")
        logger.info("[prompt_agent]   instruction: %s", revision_instruction)

        llm_prompt = f"""You are Cosual's image revision prompt engineer. The user wants to edit an existing AI-generated image.

## Original image prompt (describes what the current image looks like)
{original_prompt[:1500]}

## User's edit instruction
{revision_instruction}

## Your task
Write a short, precise edit prompt (1-3 sentences) that tells the image-edit model EXACTLY what to change.
- Reference the specific elements from the original image that need changing.
- Be direct and actionable (e.g. "Change the background color from white to dark navy blue" not "make it darker").
- Do NOT describe the entire image — only describe the changes.
- Output ONLY the edit prompt text. No preamble."""

        result = await call_qwen(llm_prompt, agent_name="prompt_agent", enable_thinking=False)
        logger.info("[prompt_agent] ✅ Revision edit prompt generated (%d chars)", len(result))
        return {**state, "generated_prompt": result.strip()}

    # ── Normal generation mode ────────────────────────────────────────────
    concept = state.get("architecture_summary") or state["free_text"]
    style_config = state.get("style_config", {})
    output_type = style_config.get("output_type", "image")
    style = style_config.get("style", "")
    platform = style_config.get("platform", "linkedin")
    aspect_ratio = style_config.get("aspect_ratio", "16:9")
    duration = int(style_config.get("duration") or 10)

    visual_style, is_creative = _resolve_style(style)

    logger.info(
        "[prompt_agent] 🚀 Generating %s prompt (style='%s', creative=%s)",
        output_type, style, is_creative,
    )

    if not is_creative:
        # Build prompt directly — no LLM, no hallucination risk
        if output_type == "image":
            result = await _build_diagram_image_prompt(concept, aspect_ratio, platform)
        else:
            result = _build_diagram_video_prompt(concept, aspect_ratio, duration, platform)
        logger.info("[prompt_agent] ✅ Diagram prompt built directly (%d chars)", len(result))

    else:
        # Creative style — use LLM but with strict guardrails
        composition = ASPECT_RATIO_COMPOSITION.get(aspect_ratio, "balanced layout")

        if output_type == "image":
            llm_prompt = f"""You are a prompt engineer for AI image generation models.

## Concept
{concept[:1000]}

## Style (strictly follow this — do not add elements outside this style)
{visual_style}

## Layout
{composition}

## Rules
- Stay strictly within the requested style. Do not add elements from other styles.
- The image must still be recognizable as a representation of the software concept above.
- Include: subject, color palette (3-4 specific colors), lighting, mood, quality tags.
- Do NOT include: humans, 3D renders unless style requires it, unrelated decorative elements.
- Quality tags to append: "ultra-detailed, sharp focus, high resolution, professional"

Output a SINGLE paragraph (100-180 words). Raw prompt text only."""

        else:
            num_shots = {5: 3, 10: 4, 15: 5}.get(duration, 4)
            llm_prompt = f"""You are a prompt engineer for AI video generation (Wan2.6 multi-shot).

## Concept
{concept[:1000]}

## Style (strictly follow this)
{visual_style}

## Layout
{composition}

## Rules
- {num_shots} shots totaling {duration} seconds
- Each shot: timing, camera movement, what is shown, transition
- Stay within the requested style — no elements from other styles
- The video must still represent the software concept above

Output ONLY the storyboard in this format, no preamble:
Shot 1 [0-Xs]: [description]. Transition: [type].
Shot 2 [X-Ys]: [description]. Transition: [type]."""

        result = await call_qwen(llm_prompt, agent_name="prompt_agent", enable_thinking=True)
        logger.info("[prompt_agent] ✅ Creative prompt from LLM (%d chars)", len(result))

    return {**state, "generated_prompt": result.strip()}
