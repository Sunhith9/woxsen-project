# ─────────────────────────────────────────────────────────────────────────────
# Woxsen RAG Backend – Dockerfile
# ─────────────────────────────────────────────────────────────────────────────
# Multi-stage build:
#   builder – installs Python wheels (avoids build tools in final image)
#   runtime – lean production image
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Install build deps (needed for some native wheels like pydantic-core)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt \
 && pip wheel --no-cache-dir --wheel-dir /wheels gunicorn

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Create non-root user
RUN useradd -m -u 1000 appuser

# Install curl for health-check only
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pre-built wheels and install without recompiling
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links /wheels /wheels/*.whl \
    && rm -rf /wheels

# Copy application source
COPY . .

# Ensure chroma_db directory exists and is writable
RUN mkdir -p /app/chroma_db && chown -R appuser:appuser /app

USER appuser

# Number of Gunicorn workers (override via env: WORKERS=4)
ENV WORKERS=4 \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Use Gunicorn + UvicornWorker for multi-process concurrency
CMD ["sh", "-c", \
     "gunicorn backend.main:app \
      --workers ${WORKERS} \
      --worker-class uvicorn.workers.UvicornWorker \
      --bind ${HOST}:${PORT} \
      --timeout 120 \
      --keepalive 5 \
      --access-logfile - \
      --error-logfile -"]
