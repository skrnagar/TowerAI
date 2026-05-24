# AI Engine — GPU-enabled base image
# Use runtime image for production GPU deployments
FROM python:3.11-slim AS base

WORKDIR /app

# OpenCV and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /models /data/screenshots

EXPOSE 8001

CMD ["python", "-m", "app.main"]

# GPU variant — uncomment and use for NVIDIA deployments
# FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04 AS gpu
# ... (install Python 3.11, PyTorch with CUDA, then copy app)
