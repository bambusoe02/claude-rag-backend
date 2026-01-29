from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from anthropic import Anthropic
import chromadb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Claude RAG API",
    description="Production-ready RAG chatbot using Claude API",
    version="1.0.0"
)

# CORS for Next.js frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients (lazy - will be created when needed)
anthropic_client = None
chroma_client = None
collection = None

def get_anthropic_client():
    """Get or create Anthropic client"""
    global anthropic_client
    if anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        anthropic_client = Anthropic(api_key=api_key)
    return anthropic_client

def get_chroma_collection():
    """Get or create ChromaDB collection"""
    global chroma_client, collection
    if chroma_client is None:
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection = chroma_client.get_or_create_collection(name="documents")
    return collection

@app.get("/")
async def root():
    return {
        "status": "Claude RAG API running",
        "version": "1.0.0",
        "model": "claude-sonnet-4-20250514"
    }

# Health check endpoint for Railway (must work even if other services fail)
@app.get("/health")
async def health():
    """Health check endpoint for Railway deployment."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "claude-rag-api"}
    )

# Import routers (after health check is defined)
try:
    from routers import upload, chat, documents
    app.include_router(upload.router)
    app.include_router(chat.router)
    app.include_router(documents.router)
except Exception as e:
    # Log error but don't crash - health check should still work
    print(f"Warning: Failed to import routers: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

