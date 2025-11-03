# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (optional minimal)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# App source
COPY src /app/src

# Expose default port (Render provides $PORT)
EXPOSE 8000

# Start server
# Use shell form to allow PORT environment variable expansion
CMD uvicorn src.app:app --host 0.0.0.0 --port ${PORT:-8000}
