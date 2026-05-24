# Tower AI Safety Monitoring System

Enterprise AI-powered industrial safety monitoring platform for telecom towers, transmission infrastructure, wind turbine construction, and work-at-height operations.

## Overview

Tower AI monitors workers via CCTV/IP cameras and automatically detects safety violations in real time — functioning as an AI EHS Command Center for remote outdoor industrial deployments.

### Phase 1 MVP Capabilities

| Feature | Status |
|---------|--------|
| Worker Detection | Architecture Ready |
| Helmet Detection | Architecture Ready |
| Harness Detection | Architecture Ready |
| Restricted Area Detection | Architecture Ready |
| Live Camera Streaming | Architecture Ready |
| Dashboard | Foundation Built |
| Alert System | Architecture Ready |
| Incident Logging | Architecture Ready |

## Architecture

```
CAMERA (RTSP/IP)
       ↓
RTSP STREAM PROCESSOR
       ↓
FRAME QUEUE (Redis)
       ↓
AI INFERENCE ENGINE (YOLOv11)
       ↓
DEEPSORT TRACKING
       ↓
VIOLATION RULE ENGINE
       ↓
ALERT ENGINE (Celery)
       ↓
PostgreSQL + MinIO
       ↓
WebSocket → Dashboard
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.11, WebSocket, Celery |
| AI Engine | YOLOv11, OpenCV, PyTorch, DeepSORT |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Storage | MinIO (S3-compatible) |
| Infrastructure | Docker, Docker Compose, Nginx |

## Project Structure

```
towerai/
├── frontend/          # Next.js 15 dashboard
├── backend/           # FastAPI REST + WebSocket API
├── ai-engine/         # YOLO inference + tracking pipeline
├── infrastructure/    # Nginx, PostgreSQL init scripts
├── docker/            # Dockerfiles for all services
├── docs/              # Architecture, schema, roadmap
├── scripts/           # Dev and deployment scripts
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (local frontend dev)
- Python 3.11+ (local backend dev)
- NVIDIA GPU + CUDA (optional, for AI acceleration)

### Setup

```bash
# Clone and configure
cp .env.example .env

# Start all services
make up

# Run database migrations
make migrate

# View logs
make logs
```

### Access Points

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| AI Engine | http://localhost:8001/docs |
| MinIO Console | http://localhost:9001 |
| Nginx Proxy | http://localhost |

### Default Credentials

- **Admin**: `admin@towerai.local` / `Admin@123`
- **MinIO**: `towerai_minio` / `towerai_minio_secret`

## API Endpoints

```
POST   /api/v1/auth/login
GET    /api/v1/auth/me
GET    /api/v1/cameras
POST   /api/v1/cameras
GET    /api/v1/violations
POST   /api/v1/violations
GET    /api/v1/alerts
GET    /api/v1/dashboard/stats
WS     /ws
WS     /ws/alerts
WS     /ws/cameras/{camera_id}
```

## Development

```bash
# Backend (local)
make dev-backend

# Frontend (local)
make dev-frontend

# AI Engine (local)
make dev-ai

# Run tests
make test-backend
make test-ai
```

## Supabase

- Project: `edwdhyoghxnqrgzrocol`
- Setup guide: [docs/SUPABASE.md](./docs/SUPABASE.md)
- Frontend env: `frontend/.env.local` (copy from `.env.local.example`)

```bash
brew install supabase/tap/supabase
supabase login
supabase link --project-ref edwdhyoghxnqrgzrocol
```

## Documentation

- [Architecture](./docs/ARCHITECTURE.md) — System design and service interactions
- [Supabase](./docs/SUPABASE.md) — Auth, DB, CLI, MCP
- [Blueprint v2.0 Alignment](./docs/BLUEPRINT_V2_ALIGNMENT.md) — 99% accuracy blueprint mapped to repo
- [Accuracy Roadmap](./docs/ACCURACY_ROADMAP.md) — 80% → 99% milestone plan
- [Prompt Library](./docs/PROMPT_LIBRARY.md) — Annotator, VLM, alert, and ops prompts
- [Database Schema](./docs/DATABASE_SCHEMA.md) — Full PostgreSQL schema reference
- [Development Roadmap](./docs/DEVELOPMENT_ROADMAP.md) — Phase 1 step-by-step plan

## AI Training (Blueprint v2.0)

```bash
cd ai-engine
pip install ultralytics roboflow opencv-python-headless
python training/train_phase1.py --data dataset/data.yaml
python training/train_phase2.py
python training/validate_model.py
```

## License

Proprietary — KEC Tower AI Safety Platform
