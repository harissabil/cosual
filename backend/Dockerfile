# ── Cosual Backend — Production Dockerfile ────────────────────────────────────
# Uses uv for fast, reproducible dependency installation.
# Multi-stage build: install deps first (cached), then copy app code.

FROM python:3.13-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# ── Stage 1: Install dependencies (cached unless pyproject.toml/uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ── Stage 2: Copy application code
COPY . .

# Create storage directories
RUN mkdir -p storage/images storage/videos

# Expose the API port
EXPOSE 8000

# Run with uv so the virtualenv is activated automatically
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--root-path", "/api"]