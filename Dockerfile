# Multi-stage build for faster Railway deployments
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies only (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip (single command)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install all dependencies in one go (faster than splitting)
# Use --no-build-isolation for faster builds
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Production stage - minimal image
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder (optimized - single copy)
COPY --from=builder /usr/local /usr/local

# Copy application code (only necessary files)
COPY main.py .
COPY routers/ ./routers/
COPY rag/ ./rag/
COPY services/ ./services/

# Create necessary directories
RUN mkdir -p chroma_db

# Expose port
EXPOSE 8000

# Note: Health check handled by Railway, not Docker HEALTHCHECK

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

