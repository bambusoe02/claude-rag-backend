# Railway Build Timeout Fix

## Problem
The Docker build completes successfully but times out during the "importing to docker" phase when Railway pushes the image to their registry. This happens because the final image is very large (~2-3GB) due to dependencies like:
- PyTorch (~900MB)
- CUDA libraries (~1.5GB)
- ChromaDB and other ML libraries

## Solutions Applied

### 1. Optimized Dockerfile
- Added aggressive cleanup of Python cache files, test directories, and documentation
- Removed temporary files and pip cache
- Kept package metadata (dist-info) to avoid breaking dependencies

### 2. Enhanced .dockerignore
- Excluded more unnecessary files from build context
- Reduced build context size

## Additional Solutions to Try

### Option 1: Contact Railway Support
Railway may be able to increase your build timeout limit. Contact support with:
- Your project name
- Build logs showing successful completion but timeout during push
- Request for increased build timeout or image push timeout

### Option 2: Use Railway's NIXPACKS Builder
Switch from Dockerfile to NIXPACKS which may handle large dependencies better:

1. Remove or rename `railway.toml` temporarily
2. Update `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### Option 3: Use CPU-Only PyTorch (if GPU not needed)
If you don't need GPU support on Railway, modify `requirements.txt` to use CPU-only torch:

```txt
# Replace sentence-transformers with CPU-only dependencies
# Or use torch-cpu instead of torch
```

However, this may require changes to your code if it expects GPU.

### Option 4: Split Dependencies
Install heavy dependencies (torch, chromadb) separately or use pre-built images, though this is complex.

### Option 5: Use External Vector Database
Consider using a managed ChromaDB service or alternative (Pinecone, Weaviate) to reduce image size.

## Current Status
The Dockerfile has been optimized to reduce image size. Try deploying again. If it still times out, try Option 1 (contact Railway support) or Option 2 (switch to NIXPACKS).

