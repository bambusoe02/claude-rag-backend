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

# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

@app.get("/")
async def root():
    return {
        "status": "Claude RAG API running",
        "version": "1.0.0",
        "model": "claude-sonnet-4-20250514"
    }

# Health check endpoint for Railway
@app.get("/health")
async def health():
    """Health check endpoint for Railway deployment."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "claude-rag-api"}
    )

# Import routers
from routers import upload, chat, documents
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(documents.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

