# Check Railway Logs for Upload Error

## Current Issue
Backend returns: "Error processing document. Please try again."

## What to Check in Railway Logs

1. **Go to Railway Dashboard:**
   - https://railway.app
   - Select `claude-rag-backend`
   - Click **Deploy Logs** or **HTTP Logs**

2. **Look for these specific errors:**

### During Upload Request:
- `[UPLOAD] Received upload request for file: ...`
- `[UPLOAD] Parsing document...`
- `[UPLOAD] Chunking text...`
- `[UPLOAD] Generating embeddings...`
- **ERROR HERE** - This is where it fails

### Common Error Patterns:

**If you see:**
- `ImportError: No module named 'sentence_transformers'`
  - → sentence-transformers not installed properly

- `ImportError: No module named 'torch'`
  - → torch dependency missing

- `Failed to initialize sentence-transformers`
  - → Model download failed or memory issue

- `Embedding generation error`
  - → Error during embedding creation

- `Error generating embeddings`
  - → Retry logic exhausted

3. **Copy the FULL error message and stack trace**

## Quick Fix Options

### Option 1: Use OpenAI (if you have key)
- Add `OPENAI_API_KEY` to Railway variables
- System will automatically use OpenAI instead

### Option 2: Use lighter embedding solution
- I can switch to a lighter library
- Or use a simple hash-based embedding (less accurate but works)

### Option 3: Check Railway resource limits
- Railway free tier may have memory/disk limits
- Torch + sentence-transformers needs ~2-3GB RAM

## Next Steps

1. **Check Railway logs** and copy the exact error
2. **Share the error message** so I can fix it
3. **Or** if you have OpenAI API key, add it to Railway and it will work immediately

