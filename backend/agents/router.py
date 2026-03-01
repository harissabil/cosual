"""Input Router Agent — routes to the correct next node based on state."""

import logging

from agents.state import CosualState

logger = logging.getLogger("cosual")


def route_input(state: CosualState) -> str:
    """Return the name of the next node based on the input type."""
    if state.get("github_url"):
        logger.info("[router] 🔀 Routing to → github_agent (GitHub URL detected)")
        return "github_agent"
    elif state.get("raw_code"):
        logger.info("[router] 🔀 Routing to → code_analyzer (raw code detected)")
        return "code_analyzer"
    else:
        logger.info("[router] 🔀 Routing to → prompt_agent (text-only input)")
        return "prompt_agent"


async def input_router_node(state: CosualState) -> CosualState:
    """No-op node — routing is done via conditional edges."""
    logger.info("[router] 🚀 Input router started for job %s", state.get("job_id", "?"))
    return state
