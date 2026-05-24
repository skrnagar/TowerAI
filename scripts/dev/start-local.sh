#!/usr/bin/env bash
# Start Tower AI locally: backend (8000), frontend (3000), AI engine (8001)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

./scripts/dev/sync-env.sh

echo ""
echo "Tower AI — local stack"
echo "  Dashboard:  http://localhost:3000"
echo "  API docs:   http://localhost:8000/docs"
echo "  AI engine:  http://localhost:8001/health"
echo "  Login:      admin@towerai.com or admin@towerai.local / Admin@123"
echo ""

port_busy() { lsof -i ":$1" >/dev/null 2>&1; }

start_backend() {
  if port_busy 8000; then
    echo "[backend] already on :8000"
    return
  fi
  (
    cd "$ROOT/backend"
    source .venv/bin/activate 2>/dev/null || true
    exec uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ) &
  echo "[backend] started pid $! → http://127.0.0.1:8000"
}

start_frontend() {
  if port_busy 3000; then
    echo "[frontend] already on :3000"
    return
  fi
  (
    cd "$ROOT/frontend"
    exec npm run dev
  ) &
  echo "[frontend] started pid $! → http://localhost:3000"
}

start_ai() {
  if port_busy 8001; then
    echo "[ai-engine] already on :8001"
    return
  fi
  if ! python3 -c "import ultralytics" 2>/dev/null; then
    echo "[ai-engine] SKIP — install: cd ai-engine && pip install -r requirements.txt"
    return
  fi
  (
    cd "$ROOT/ai-engine"
    export YOLO_MODEL_PATH="${YOLO_MODEL_PATH:-yolov8n.pt}"
    export AI_GPU_ENABLED="${AI_GPU_ENABLED:-true}"
    export BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
    exec python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001
  ) &
  echo "[ai-engine] started pid $! → http://127.0.0.1:8001"
}

start_backend
start_frontend
start_ai

sleep 2
echo ""
curl -sf http://127.0.0.1:8000/health >/dev/null && echo "✓ backend health" || echo "✗ backend not ready"
curl -sf http://127.0.0.1:3000 >/dev/null 2>&1 && echo "✓ frontend" || echo "… frontend still starting"
curl -sf http://127.0.0.1:8001/health >/dev/null 2>&1 && echo "✓ ai-engine health" || echo "… ai-engine optional / still starting"

echo ""
echo "Demo detection on a downloaded video:"
echo "  cd ai-engine && python3 scripts/demo_video_detect.py --video dataset/raw/videos/K6YHA3p3APM.f136.mp4 --max-frames 30"
echo ""
echo "Press Ctrl+C to stop this script (child processes may keep running — use: pkill -f 'uvicorn app.main' or close terminals)"

wait
