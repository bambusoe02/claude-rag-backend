# Multi-stage build optimized for Railway (reduced size + faster builds)
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

# Clean up pip cache and unnecessary files to reduce image size
# Remove Python cache files, test files, and documentation (but keep dist-info for package metadata)
RUN find /usr/local -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true && \
    find /usr/local -type f -name "*.pyc" -delete && \
    find /usr/local -type f -name "*.pyo" -delete && \
    find /usr/local -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local -type f -name "*.md" -not -path "*/dist-info/*" -delete 2>/dev/null || true && \
    rm -rf /root/.cache/pip /tmp/* /var/tmp/*

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

# Note: chroma_db will be created at runtime or mounted via Railway Volume
# No need to create it in the image to reduce size

# Expose port
EXPOSE 8000

# Note: Health check handled by Railway, not Docker HEALTHCHECK

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

