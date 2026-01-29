# Claude RAG Backend

Production-ready RAG chatbot backend using FastAPI + Claude API + ChromaDB.

## Features

- ✅ FastAPI with async support
- ✅ Claude Sonnet 4 integration
- ✅ ChromaDB vector store
- ✅ Document parsing (PDF, TXT, MD, DOCX)
- ✅ Smart text chunking with overlap
- ✅ Semantic search with embeddings
- ✅ Source citations
- ✅ CORS enabled for Next.js frontend

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Run the server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- `GET /` - API status
- `GET /health` - Health check

### Upload
- `POST /api/upload/document` - Upload and process document

### Chat
- `POST /api/chat/message` - Send message and get RAG response

### Documents
- `GET /api/documents/list` - List all documents
- `GET /api/documents/stats` - Get collection statistics
- `DELETE /api/documents/{doc_id}` - Delete document

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Railway

1. Connect GitHub repo
2. Add `ANTHROPIC_API_KEY` environment variable
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

## Architecture

```
backend/
├── main.py              # FastAPI app
├── routers/             # API routes
│   ├── upload.py
│   ├── chat.py
│   └── documents.py
├── rag/                 # RAG components
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   └── claude_chain.py
└── services/            # Utilities
    ├── parser.py
    └── chunker.py
```

