# ---- Stage 1: builder -----------------------------------------------------
FROM python:3.12-slim AS builder

# System build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Install Python dependencies into a prefix so we can copy them cleanly
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ---- Stage 2: runtime -----------------------------------------------------
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="PeopleDoxx API" \
      org.opencontainers.image.description="OSINT aggregator for Ecuadorian public government portals" \
      org.opencontainers.image.version="1.0.0"

# Runtime system dependencies (libpq for asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ app/

# Fix ownership
RUN chown -R appuser:appuser /app

USER appuser

# Expose the API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx, sys; r = httpx.get('http://localhost:8000/health', timeout=5); sys.exit(0 if r.status_code == 200 else 1)"

# Start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
