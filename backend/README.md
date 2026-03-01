# Cosual Backend

AI-powered content generator that transforms code concepts into visuals — architecture diagrams, video descriptions — with captions tailored for LinkedIn or Instagram.

## Tech Stack

- **Framework:** FastAPI
- **LLM / AI SDK:** dashscope (Alibaba Cloud Model Studio)
- **Agent Orchestration:** LangGraph
- **Database:** SQLite via aiosqlite + SQLAlchemy (async)
- **Package Manager:** uv

## Setup

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn main:app --reload --port 8000
```

## Docker

```bash
# Build the image
docker build -t cosual-backend .

# Run the container
docker run -d \
  --name cosual-backend \
  -p 8000:8000 \
  -e DASHSCOPE_API_KEY=your-api-key-here \
  -v cosual-storage:/app/storage \
  cosual-backend
```

The `-v cosual-storage:/app/storage` flag persists generated images and videos across container restarts.

To use an `.env` file instead of passing variables individually:

```bash
docker run -d \
  --name cosual-backend \
  -p 8000:8000 \
  --env-file .env \
  -v cosual-storage:/app/storage \
  cosual-backend
```

API docs available at `http://localhost:8000/docs` once running.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/generate` | Start a new generation job |
| GET | `/status/{job_id}` | Poll job status |
| POST | `/revise/{job_id}` | Revise an image job |
| GET | `/history` | List all jobs |
| GET | `/history/{job_id}` | Get job details with revisions |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DASHSCOPE_API_KEY` | Alibaba Cloud Model Studio API key |
| `DATABASE_URL` | SQLite connection string |
