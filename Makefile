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

dev-backend: ## Run backend locally (requires local venv)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend locally
	cd frontend && npm run dev

dev-ai: ## Run AI engine locally
	cd ai-engine && python -m app.main

dataset-download: ## Download reference YouTube videos
	cd ai-engine && python3 scripts/download_videos.py

dataset-frames: ## Extract frames at 1 FPS from downloaded videos
	cd ai-engine && python3 scripts/extract_frames.py --layout

dataset-preview: ## Smoke-test YOLO on one extracted frame
	cd ai-engine && python3 scripts/preview_frames.py
