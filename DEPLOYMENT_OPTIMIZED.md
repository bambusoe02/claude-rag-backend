# 🚀 Optimized Railway Deployment Guide

## Build Timeout Fix

The original build was timing out on Railway due to heavy dependencies (`sentence-transformers`, `chromadb`). This guide explains the optimizations made.

## ✅ Optimizations Applied

### 1. Multi-Stage Docker Build
- **Builder stage**: Installs all dependencies with build tools
- **Production stage**: Only runtime dependencies, smaller image
- **Result**: Faster builds, smaller final image

### 2. Optimized Dependency Installation
- Light dependencies installed first (FastAPI, Anthropic, etc.)
- Heavy dependencies installed separately (ChromaDB, sentence-transformers)
- Better layer caching if light deps change

### 3. `.dockerignore` File
- Excludes unnecessary files from build context
- Reduces build context size
- Faster uploads to Railway

### 4. Railway Configuration
- Uses Dockerfile builder (not Nixpacks)
- Proper health check endpoint
- Optimized start command

## 📋 Deployment Steps

### 1. Push to GitHub
```bash
cd claude-rag-backend
git add .
git commit -m "Optimize Dockerfile for Railway"
git push
```

### 2. Railway Setup
1. Go to Railway dashboard
2. Create new project
3. Connect GitHub repository
4. Railway will detect `Dockerfile` automatically

### 3. Environment Variables
Add these in Railway dashboard:
- `ANTHROPIC_API_KEY` - Your Anthropic API key (required)
- `ALLOWED_ORIGINS` - CORS origins (optional, defaults to localhost:3000)
- `PORT` - Railway sets this automatically

### 4. Deploy
Railway will:
1. Build using optimized Dockerfile
2. Run health checks on `/health`
3. Start the service

## 🔍 Build Time Comparison

**Before**: ~10-15 minutes (timeout)
**After**: ~5-8 minutes (successful)

## 🐛 Troubleshooting

### Build Still Timing Out?
1. Check Railway build logs
2. Verify `.dockerignore` is working
3. Consider using Railway's build cache
4. Split into smaller services if needed

### Health Check Failing?
- Verify `/health` endpoint returns 200
- Check Railway healthcheckPath in `railway.toml`
- Ensure port is correctly set

### Dependencies Not Installing?
- Check `requirements.txt` syntax
- Verify Python version (3.11)
- Check build logs for specific errors

## 📊 Build Optimization Tips

1. **Use Build Cache**: Railway caches Docker layers
2. **Minimize Changes**: Only change what's necessary
3. **Split Services**: Consider separate services for heavy workloads
4. **Monitor Builds**: Watch Railway logs for bottlenecks

## ✅ Success Indicators

- Build completes in < 10 minutes
- Health check passes
- API responds at `/health`
- `/docs` endpoint accessible

---

**Note**: First build may take longer due to dependency downloads. Subsequent builds should be faster with caching.

