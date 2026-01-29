# How to Get Railway Logs

## Method 1: Railway Dashboard (Easiest)

1. **Go to Railway Dashboard:**
   - https://railway.app
   - Login to your account

2. **Select your project:**
   - Click on `claude-rag-backend`

3. **View Logs:**
   - Click on **"Deploy Logs"** tab (for build/deploy logs)
   - OR click on **"HTTP Logs"** tab (for runtime/request logs)
   - OR click on **"Logs"** in the sidebar

4. **Filter for upload errors:**
   - In the logs, look for:
     - `[UPLOAD]` - Upload processing logs
     - `[ERROR]` - Error messages
     - `Error processing document` - The actual error
     - Stack traces (lines starting with `Traceback`)

5. **Copy the relevant section:**
   - Select the error section
   - Copy and paste here

## Method 2: Railway CLI (If installed)

```bash
railway logs --service claude-rag-backend
```

## Method 3: Download Logs

1. In Railway Dashboard → Logs
2. Click the download icon (usually top right)
3. Select time range
4. Download logs

## What to Look For

When you upload a file, you should see in logs:

```
[UPLOAD] Received upload request for file: test.pdf
[UPLOAD] File size: 12345 bytes
[UPLOAD] Parsing document...
[UPLOAD] Parsed content length: 5000 characters
[UPLOAD] Chunking text...
[UPLOAD] Created 5 chunks
[UPLOAD] Generating embeddings...
[ERROR] <-- Error will appear here
```

## Common Errors to Look For

1. **Import errors:**
   - `No module named 'sentence_transformers'`
   - `No module named 'torch'`
   - `No module named 'config'`

2. **Memory errors:**
   - `MemoryError`
   - `Out of memory`
   - `Killed` (process killed due to memory)

3. **Model download errors:**
   - `Failed to download model`
   - `Connection timeout`
   - `Model not found`

4. **Embedding errors:**
   - `Error generating embeddings`
   - `Embedding generation timeout`
   - `Failed to initialize sentence-transformers`

## Quick Test

1. Try uploading a file
2. Immediately check Railway logs
3. Look for the error message
4. Copy the FULL error (including stack trace)

