# Multi-stage Dockerfile for MCP Web Search Server
# Supports both development and production deployments

# =============================================================================
# Base Stage: Common dependencies and setup
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install core Python dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.110.0 \
    fastapi-mcp>=0.1.0 \
    uvicorn>=0.27.0 \
    httpx>=0.27.0 \
    pydantic>=2.5.0 \
    python-dotenv>=1.0.0 \
    google-api-python-client>=2.100.0

# =============================================================================
# Development Stage: Hot reload, debugging tools
# =============================================================================
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest>=7.0.0 \
    pytest-asyncio>=0.21.0 \
    black>=23.0.0 \
    ruff>=0.1.0 \
    watchfiles \
    uvicorn[standard]

# Copy source code (will be overridden by volume mount in development)
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Production Stage: Optimized, secure, minimal
# =============================================================================
FROM base as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Install production dependencies (if any additional ones needed)
RUN pip install --no-cache-dir gunicorn

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with Gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]