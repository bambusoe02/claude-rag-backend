# Deployment Guide

## Railway (Backend)

### Step 1: Prepare Repository
1. Push your code to GitHub
2. Ensure `railway.json` is in the root of `claude-rag-backend/`

### Step 2: Deploy to Railway
1. Go to [Railway](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Select the `claude-rag-backend` directory as the root

### Step 3: Configure Environment Variables
In Railway dashboard, add:
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `ALLOWED_ORIGINS` - Your frontend URL (e.g., `https://your-app.vercel.app`)

### Step 4: Deploy
Railway will automatically:
- Detect Python project
- Install dependencies
- Run the start command
- Provide a public URL

### Step 5: Update Frontend
Update `NEXT_PUBLIC_API_URL` in your frontend `.env.local` with the Railway URL.

## Vercel (Frontend)

### Step 1: Prepare Repository
1. Push your code to GitHub
2. Ensure `vercel.json` is in the root of `claude-rag-frontend/`

### Step 2: Deploy to Vercel
1. Go to [Vercel](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Select the `claude-rag-frontend` directory as the root

### Step 3: Configure Environment Variables
In Vercel dashboard, add:
- `NEXT_PUBLIC_API_URL` - Your Railway backend URL

### Step 4: Deploy
Vercel will automatically:
- Detect Next.js project
- Install dependencies
- Build the app
- Deploy to production

## Docker (Alternative)

### Build Backend Image
```bash
cd claude-rag-backend
docker build -t claude-rag-backend .
```

### Run Backend Container
```bash
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key \
  -e ALLOWED_ORIGINS=http://localhost:3000 \
  -v $(pwd)/chroma_db:/app/chroma_db \
  claude-rag-backend
```

### Build Frontend Image
```bash
cd claude-rag-frontend
docker build -t claude-rag-frontend .
```

### Run Frontend Container
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  claude-rag-frontend
```

## Environment Variables Summary

### Backend
- `ANTHROPIC_API_KEY` (required) - Anthropic API key
- `ALLOWED_ORIGINS` (optional) - CORS origins, comma-separated
- `CHROMA_DB_PATH` (optional) - ChromaDB path, defaults to `./chroma_db`

### Frontend
- `NEXT_PUBLIC_API_URL` (required) - Backend API URL

## Troubleshooting

### Backend Issues
- **Port already in use**: Change port in `railway.json` or use `$PORT` environment variable
- **ChromaDB errors**: Ensure write permissions for `chroma_db` directory
- **API key errors**: Verify `ANTHROPIC_API_KEY` is set correctly

### Frontend Issues
- **API connection errors**: Check `NEXT_PUBLIC_API_URL` matches backend URL
- **CORS errors**: Add frontend URL to backend `ALLOWED_ORIGINS`
- **Build errors**: Ensure all dependencies are installed

## Monitoring

### Railway
- View logs in Railway dashboard
- Set up alerts for errors
- Monitor resource usage

### Vercel
- View logs in Vercel dashboard
- Monitor analytics
- Set up webhooks for deployments

