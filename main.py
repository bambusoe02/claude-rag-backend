from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log startup info
logger.info("Starting FastAPI application...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")

app = FastAPI(
    title="Claude RAG API",
    description="Production-ready RAG chatbot using Claude API",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS for Next.js frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
logger.info(f"[CORS] Allowed origins: {allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Railway and Kubernetes (must work even if other services fail)
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway and Kubernetes deployments."""
    return {
        "status": "healthy",
        "service": "claude-rag-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    return {
        "status": "Claude RAG API running",
        "version": "1.0.0",
        "model": "claude-sonnet-4-20250514"
    }

# Initialize clients (lazy - will be created when needed)
anthropic_client = None

def get_anthropic_client():
    """Get or create Anthropic client"""
    global anthropic_client
    if anthropic_client is None:
        from anthropic import Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        # Temporarily unset proxy environment variables to prevent Anthropic/httpx from using them
        # Anthropic 0.39.0 doesn't support 'proxies' parameter in constructor
        original_proxies = {}
        proxy_vars = [
            'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
            'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy'
        ]
        
        for var in proxy_vars:
            if var in os.environ:
                original_proxies[var] = os.environ.pop(var)
        
        try:
            # Only pass api_key - Anthropic 0.39.0 doesn't support additional parameters like proxies
            anthropic_client = Anthropic(api_key=api_key)
            logger.info("Anthropic client initialized successfully (proxies disabled)")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
        finally:
            # Restore proxy environment variables if they were set
            for var, value in original_proxies.items():
                os.environ[var] = value
    return anthropic_client

# ChromaDB client is now managed by rag.chroma_client module
from rag.chroma_client import get_chroma_collection

# Validate required environment variables at startup
@app.on_event("startup")
async def startup_event():
    """Validate required environment variables on startup"""
    required_vars = ["ANTHROPIC_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}"
        logger.error(error_msg)
        logger.error("Please set these variables in your .env file or environment")
        # Don't raise - allow health check to work, but log error
        logger.warning("Application started but may not function correctly without required API keys")
    else:
        logger.info("✅ All required environment variables are set")
    
    # Check for optional OpenAI API key (for embeddings)
    if os.getenv("OPENAI_API_KEY"):
        logger.info("✅ OPENAI_API_KEY found - will use OpenAI embeddings")
    else:
        logger.info("ℹ️  OPENAI_API_KEY not set - will use sentence-transformers (local, free embeddings)")

# Import routers (after health check is defined)
try:
    from routers import upload, chat, documents
    app.include_router(upload.router)
    app.include_router(chat.router)
    app.include_router(documents.router)
except Exception as e:
    # Log error but don't crash - health check should still work
    import traceback
    logger.warning(f"Failed to import routers: {str(e)}")
    logger.debug(traceback.format_exc())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

