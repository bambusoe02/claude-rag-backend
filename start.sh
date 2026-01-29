#!/bin/bash
set -e

# Get port from Railway environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting FastAPI application on port $PORT"

# Start uvicorn
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"

