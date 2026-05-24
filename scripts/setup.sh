#!/usr/bin/env bash
# Tower AI — Development environment setup script
set -euo pipefail

echo "=== Tower AI Safety Monitoring System — Setup ==="

# Copy environment file if not exists
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✓ Created .env from .env.example"
  echo "  ⚠ Update SECRET_KEY and JWT_SECRET_KEY before production!"
else
  echo "✓ .env already exists"
fi

# Create required directories
mkdir -p ai-engine/models
mkdir -p data/screenshots
mkdir -p data/recordings
mkdir -p logs
echo "✓ Created data directories"

# Build and start services
echo ""
echo "Starting Docker services..."
docker compose build
docker compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Health checks
echo ""
echo "=== Health Checks ==="
curl -sf http://localhost:8000/health && echo "✓ Backend healthy" || echo "✗ Backend not ready"
curl -sf http://localhost:8001/health && echo "✓ AI Engine healthy" || echo "✗ AI Engine not ready"
curl -sf http://localhost:3000 > /dev/null && echo "✓ Frontend healthy" || echo "✗ Frontend not ready"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Access points:"
echo "  Dashboard:    http://localhost:3000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  AI Engine:    http://localhost:8001/docs"
echo "  MinIO Console: http://localhost:9001"
echo ""
echo "Default login: admin@towerai.local / Admin@123"
