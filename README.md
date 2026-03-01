# Cosual

AI-powered content generator that transforms code concepts into stunning visuals — architecture diagrams, cinematic video trailers — with captions tailored for LinkedIn, Instagram, or TikTok.

Built with **Vue 3** + **FastAPI** + **LangGraph** + **Alibaba Cloud Model Studio (DashScope)**.

![Vue](https://img.shields.io/badge/Vue_3-4FC08D?style=flat&logo=vue.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Alibaba Cloud](https://img.shields.io/badge/Alibaba_Cloud-FF6A00?style=flat&logo=alibaba-cloud&logoColor=white)

## Table of Contents
- [Features](#features)
- [AI Workflow](#ai-workflow)
- [Quick Start — Deploy to Alibaba Simple Application Server](#quick-start--deploy-to-alibaba-simple-application-server)
- [Set Up a Domain with SSL (Optional)](#set-up-a-domain-with-ssl-optional)
- [Environment Variables](#environment-variables)
- [Tech Stack](#tech-stack)
- [Local Development](#local-development)
- [License](#license)

## Features

- **GitHub Repo → Visual**: Paste a repo URL and get an architecture diagram or video trailer
- **Code → Visual**: Drop in raw code and see it transformed into visuals
- **Text → Visual**: Describe a concept in plain text and generate content
- **Image & Video Generation**: Produces diagrams, illustrations, and cinematic video clips
- **Smart Captions**: Auto-generates platform-specific captions (LinkedIn, Instagram, TikTok)
- **Revision System**: Iteratively refine generated images via natural language instructions
- **Job History**: Browse and revisit all past generations

## AI Workflow

<img width="852" height="721" alt="cosual-ai-diagram drawio(5)" src="https://github.com/user-attachments/assets/5232645a-4663-4d72-808d-6accf6d6f10f" />

## Quick Start — Deploy to Alibaba Simple Application Server

### Prerequisites

- A server running **Ubuntu 20.04+** (e.g. Alibaba Cloud Simple Application Server)
- **Alibaba Cloud DashScope API key** — get one from [Model Studio](https://dashscope.console.aliyun.com/)

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

## Set Up a Domain with SSL (Optional)

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

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Tailwind CSS, CodeMirror 6, Pinia, Vue Router |
| Backend | FastAPI, LangGraph, SQLAlchemy (async), aiosqlite |
| AI / LLM | DashScope (Qwen and Wan) |
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
