"""Cosual Backend — FastAPI application entrypoint."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.generate import router as generate_router
from api.history import router as history_router
from api.revise import router as revise_router
from database.connection import init_db
from utils.file_storage import ensure_storage_dirs

# ── Configure logging ────────────────────────────────────────────────────────
# All agent/pipeline logs go through the "cosual" logger and print to terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
# Set the cosual logger level (DEBUG to see full prompts/responses)
logging.getLogger("cosual").setLevel(logging.INFO)
# Quiet down noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("dashscope").setLevel(logging.WARNING)

logger = logging.getLogger("cosual")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Cosual Backend starting up...")
    ensure_storage_dirs()
    await init_db()
    logger.info("✅ Database initialized, storage directories ready")
    logger.info("🌐 API docs available at http://localhost:8000/docs")
    yield
    logger.info("👋 Cosual Backend shutting down...")


app = FastAPI(
    title="Cosual Backend",
    description="AI-powered content generator — code concepts to stunning visuals",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files — serve generated images and videos
app.mount("/files", StaticFiles(directory="storage"), name="files")

# API routes
app.include_router(generate_router)
app.include_router(history_router)
app.include_router(revise_router)
