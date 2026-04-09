# ──────────────────────────────────────────────
# Stage 1 – builder: install Python deps into
#            a clean prefix so we can copy only
#            the wheel artifacts to the final image
# ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Don't write .pyc files and disable output buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install build tools required by some wheels (e.g. crewai C extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip in isolation before installing project deps
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ──────────────────────────────────────────────
# Stage 2 – runtime: lean image with no build tools
# ──────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # tell Python where our installed packages live
    PYTHONPATH=/app

# Create a non-root user for security best-practice
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Pull compiled packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source (knowledge_repo is mounted at runtime via a volume)
COPY app/ ./app/

# Create the knowledge repo directory owned by the app user
RUN mkdir -p /app/knowledge_repo && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Healthcheck – Docker / ECS / Kubernetes will poll this
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Use exec form so signals (SIGTERM) propagate correctly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
