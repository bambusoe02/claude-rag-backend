from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser import parse_document
from services.chunker import chunk_text
from rag.embeddings import get_embeddings
from rag.vector_store import store_documents
import uuid
from typing import Dict, Any

router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("/document")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and process document for RAG"""
    
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.txt', '.md', '.docx']
        if not any(file.filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # 1. Parse document
        content = await parse_document(file)
        
        if not content or len(content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Document appears to be empty or could not be parsed"
            )
        
        # 2. Chunk text
        chunks = chunk_text(content, chunk_size=1000, overlap=200)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks generated from document"
            )
        
        # 3. Generate embeddings
        embeddings = await get_embeddings(chunks)
        
        # 4. Store in vector DB
        doc_id = str(uuid.uuid4())
        await store_documents(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata={"filename": file.filename, "file_type": file.content_type}
        )
        
        return {
            "success": True,
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks": len(chunks),
            "message": f"Document processed successfully. Created {len(chunks)} chunks."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

