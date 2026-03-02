"""API key authentication dependency."""

import os

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

# Read the expected key from the environment (set in .env / docker-compose)
_API_KEY = os.getenv("COSUAL_API_KEY", "")

_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(
    api_key: str | None = Security(_header_scheme),
) -> str:
    """Validate the X-API-Key header against the configured secret.

    If COSUAL_API_KEY is empty/unset the check is skipped so local
    development without a key still works.
    """
    if not _API_KEY:
        # No key configured → open access (local dev)
        return ""
    if not api_key or api_key != _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return api_key
