# Multi-stage build for faster Railway deployments
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel for faster installs
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with optimizations
# Install lighter dependencies first, then heavy ones
# This allows better layer caching if light deps change
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        fastapi==0.115.0 \
        uvicorn[standard]==0.32.0 \
        anthropic==0.39.0 \
        python-multipart==0.0.18 \
        pydantic==2.10.3 \
        python-dotenv==1.0.1 \
        pypdf==5.1.0 \
        python-docx==1.1.2 && \
    pip install --no-cache-dir \
        chromadb==0.5.20 \
        sentence-transformers==3.3.1

# Production stage - minimal image
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p chroma_db

# Expose port
EXPOSE 8000

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

