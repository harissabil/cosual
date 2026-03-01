# Cosual

AI-powered content generator that transforms code concepts into stunning visuals — architecture diagrams, cinematic video trailers — with captions tailored for LinkedIn, Instagram, or TikTok.

Built with **Vue 3** + **FastAPI** + **LangGraph** + **Alibaba Cloud Model Studio (DashScope)**.

![Vue](https://img.shields.io/badge/Vue_3-4FC08D?style=flat&logo=vue.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Alibaba Cloud](https://img.shields.io/badge/Alibaba_Cloud-FF6A00?style=flat&logo=alibaba-cloud&logoColor=white)

---

## Features

- **GitHub Repo → Visual**: Paste a repo URL and get an architecture diagram or video trailer
- **Code → Visual**: Drop in raw code and see it transformed into visuals
- **Text → Visual**: Describe a concept in plain text and generate content
- **Image & Video Generation**: Produces diagrams, illustrations, and cinematic video clips
- **Smart Captions**: Auto-generates platform-specific captions (LinkedIn, Instagram, TikTok)
- **Revision System**: Iteratively refine generated images via natural language instructions
- **Job History**: Browse and revisit all past generations

## Architecture

```
┌───────────────────────┐       ┌────────────────────────────────────┐
│   Frontend (Vue 3)    │       │        Backend (FastAPI)            │
│   Nginx · Port 80     │──────▶│        Uvicorn · Port 8000         │
│                       │       │                                    │
│  • Vue Router (SPA)   │       │  ┌──────────────────────────────┐  │
│  • Pinia stores       │       │  │   LangGraph Agent Pipeline   │  │
│  • CodeMirror 6       │       │  │                              │  │
│  • Tailwind CSS       │       │  │  Router → Prompt → Image/    │  │
│                       │       │  │           Video → Caption     │  │
└───────────────────────┘       │  └──────────┬───────────────────┘  │
                                │             │                      │
                                │  ┌──────────▼───────────────────┐  │
                                │  │  DashScope (Alibaba Cloud)   │  │
                                │  │  • Qwen (LLM)               │  │
                                │  │  • Wanx (Image)             │  │
                                │  │  • Wanx (Video)             │  │
                                │  └──────────────────────────────┘  │
                                │                                    │
                                │  SQLite DB    Storage (images/vids)│
                                └────────────────────────────────────┘
```

## Project Structure

```
cosual/
├── docker-compose.yml          # One-command deployment
├── .env.example                # Environment variable template
├── backend/
│   ├── Dockerfile
│   ├── main.py                 # FastAPI entrypoint
│   ├── pyproject.toml          # Python dependencies (uv)
│   ├── agents/                 # LangGraph agent pipeline
│   │   ├── graph.py            # Agent graph definition
│   │   ├── router.py           # Input router agent
│   │   ├── prompt_agent.py     # Prompt generation agent
│   │   ├── image_agent.py      # Image generation (Wanx)
│   │   ├── video_agent.py      # Video generation (Wanx)
│   │   ├── caption_agent.py    # Caption generation agent
│   │   ├── github_agent.py     # GitHub repo analyzer
│   │   ├── code_analyzer.py    # Code analysis agent
│   │   └── llm.py              # DashScope LLM configuration
│   ├── api/                    # API route handlers
│   │   ├── generate.py         # POST /generate, GET /status/:id
│   │   ├── history.py          # GET /history, GET /history/:id
│   │   └── revise.py           # POST /revise/:id
│   ├── database/               # SQLAlchemy async models
│   └── utils/                  # File storage, title generation
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf              # SPA-ready nginx config
│   ├── package.json            # Node.js dependencies
│   └── src/
│       ├── App.vue             # Root component
│       ├── api/client.js       # Axios API client
│       ├── views/              # Page components
│       ├── components/         # Reusable UI components
│       ├── stores/             # Pinia state management
│       └── router/             # Vue Router config
└── README.md                   # ← You are here
```

---

## Prerequisites

- A server running **Ubuntu 20.04+** (e.g. Alibaba Cloud Simple Application Server)
- **Alibaba Cloud DashScope API key** — get one from [Model Studio](https://dashscope.console.aliyun.com/)

## Quick Start — Deploy to Alibaba Simple Application Server

### 1. Provision Your Server

1. Log in to [Alibaba Cloud Console](https://www.alibabacloud.com/)
2. Go to **Simple Application Server** → **Create Server**
3. Select **Ubuntu 22.04** (or 24.04) image
4. Choose at least **2 vCPU / 2 GB RAM** (4 GB recommended for image/video generation)
5. Open the following ports in the firewall rules:
   - **80** (HTTP — frontend)
   - **443** (HTTPS — optional, for domain + SSL)
   - **8000** (Backend API — or keep internal only if using a reverse proxy)
6. Note your server's **Public IP address**

### 2. Connect to the Server

```bash
ssh root@<YOUR_SERVER_IP>
```

### 3. Install Docker & Docker Compose

```bash
# Update system packages
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Start Docker and enable on boot
systemctl start docker
systemctl enable docker

# Verify installation
docker --version
docker compose version
```

### 4. Clone the Repository

```bash
cd /opt
git clone https://github.com/<YOUR_USERNAME>/cosual.git
cd cosual
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Fill in:

```env
# Your DashScope API key
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Your server's public IP or domain name
DOMAIN=<YOUR_SERVER_IP>
```

### 6. Build and Launch

```bash
docker compose up -d --build
```

This will:
- Build the **backend** image (Python 3.13 + FastAPI + uv)
- Build the **frontend** image (Vue 3 + Nginx)
- Start both containers with persistent volumes for database and generated files

### 7. Verify Deployment

```bash
# Check container status
docker compose ps

# Check logs
docker compose logs -f
```

Visit your app:
- **Frontend**: `http://<YOUR_SERVER_IP>`
- **Backend API docs**: `http://<YOUR_SERVER_IP>:8000/docs`

---

## Day-to-Day Operations

### View Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Frontend only
docker compose logs -f frontend
```

### Restart Services

```bash
docker compose restart
```

### Update to Latest Version

```bash
cd /opt/cosual
git pull origin main
docker compose up -d --build
```

### Stop Everything

```bash
docker compose down
```

### Reset Data (⚠️ destructive)

```bash
docker compose down -v    # Removes volumes (database + generated files)
docker compose up -d --build
```

---

## Optional: Set Up a Domain with SSL

If you have a domain name pointing to your server:

### 1. Install Certbot

```bash
apt install -y certbot python3-certbot-nginx
```

### 2. Update `docker-compose.yml`

Change the frontend port from `80:80` to `3000:80` temporarily, or stop the containers:

```bash
docker compose down
```

### 3. Get SSL Certificate

```bash
certbot certonly --standalone -d yourdomain.com
```

### 4. Set up Nginx as a Reverse Proxy on the Host

Install nginx on the host and create a config:

```bash
apt install -y nginx
nano /etc/nginx/sites-available/cosual
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend static files (generated images/videos)
    location /files/ {
        proxy_pass http://127.0.0.1:8000/files/;
        proxy_set_header Host $host;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/cosual /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

Update `docker-compose.yml` to map frontend to port `3000:80` instead of `80:80` and rebuild:

```bash
# In .env, set:
# DOMAIN=yourdomain.com

docker compose up -d --build
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DASHSCOPE_API_KEY` | ✅ | — | Alibaba Cloud Model Studio API key |
| `DOMAIN` | ✅ | `localhost` | Server public IP or domain (used at frontend build time) |
| `DATABASE_URL` | ❌ | `sqlite+aiosqlite:///./data/cosual.db` | SQLite connection string |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/generate` | Start a new generation job |
| `GET` | `/status/{job_id}` | Poll job status |
| `POST` | `/revise/{job_id}` | Revise an image job |
| `GET` | `/history` | List all jobs |
| `GET` | `/history/{job_id}` | Get job details with revision timeline |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Tailwind CSS, CodeMirror 6, Pinia, Vue Router |
| Backend | FastAPI, LangGraph, SQLAlchemy (async), aiosqlite |
| AI / LLM | DashScope (Qwen for text, Wanx for image/video) |
| Infrastructure | Docker, Docker Compose, Nginx |
| Deployment | Alibaba Cloud Simple Application Server (Ubuntu) |

## Local Development

### Backend

```bash
cd backend
cp .env.example .env    # Add your DASHSCOPE_API_KEY
uv sync
uv run uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

---

## License

MIT
