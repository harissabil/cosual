import os
from pathlib import Path

import httpx

STORAGE_BASE = Path("./storage")
IMAGES_DIR = STORAGE_BASE / "images"
VIDEOS_DIR = STORAGE_BASE / "videos"


def ensure_storage_dirs():
    """Create storage directories if they don't exist."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


async def download_and_save(url: str, local_path: str) -> str:
    """Download a file from a URL and save it locally."""
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(url)
        response.raise_for_status()
    with open(local_path, "wb") as f:
        f.write(response.content)
    return local_path
