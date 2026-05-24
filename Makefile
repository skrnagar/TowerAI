.PHONY: help up down build logs ps shell-backend shell-frontend shell-ai migrate seed test lint clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build all Docker images
	docker compose build

logs: ## Tail logs from all services
	docker compose logs -f

ps: ## Show running services
	docker compose ps

shell-backend: ## Open shell in backend container
	docker compose exec backend bash

shell-frontend: ## Open shell in frontend container
	docker compose exec frontend sh

shell-ai: ## Open shell in AI engine container
	docker compose exec ai-engine bash

migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

seed: ## Seed development data
	docker compose exec backend python -m app.scripts.seed

test-backend: ## Run backend tests
	docker compose exec backend pytest -v

test-ai: ## Run AI engine tests
	docker compose exec ai-engine pytest -v

lint-backend: ## Lint backend code
	docker compose exec backend ruff check app

clean: ## Remove containers, volumes, and build cache
	docker compose down -v --remove-orphans

dev-all: ## Start backend + frontend + AI engine locally
	chmod +x scripts/dev/*.sh && ./scripts/dev/start-local.sh

dev-sync-env: ## Copy Supabase keys from root .env to backend/.env
	chmod +x scripts/dev/sync-env.sh && ./scripts/dev/sync-env.sh

dev-backend: ## Run backend locally (requires local venv)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend locally
	cd frontend && npm run dev

dev-ai: ## Run AI engine locally
	cd ai-engine && python -m app.main

supabase-sync: ## Push migrations, gen types, deploy edge functions
	chmod +x scripts/supabase/sync.sh && ./scripts/supabase/sync.sh

supabase-push: ## Push DB migrations only
	supabase migration repair 20260524120000 --status applied 2>/dev/null || true
	supabase db push

supabase-types: ## Regenerate frontend/src/types/supabase.ts
	supabase gen types typescript --linked > frontend/src/types/supabase.ts

supabase-functions: ## Deploy edge functions
	supabase functions deploy health --no-verify-jwt
	supabase functions deploy violation-webhook --no-verify-jwt

dataset-download: ## Download reference YouTube videos
	cd ai-engine && python3 scripts/download_videos.py

dataset-frames: ## Extract frames at 1 FPS from downloaded videos
	cd ai-engine && python3 scripts/extract_frames.py --layout

dataset-preview: ## Smoke-test YOLO on one extracted frame
	cd ai-engine && python3 scripts/preview_frames.py
