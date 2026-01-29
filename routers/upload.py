from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser import parse_document
from services.chunker import chunk_text
from rag.embeddings import get_embeddings
from rag.vector_store import store_documents
from config import MAX_FILE_SIZE, ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
import uuid
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("/document")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and process document for RAG"""
    
    try:
        # Validate file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Validate MIME type
        if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
            logger.warning(f"File {file.filename} has unexpected MIME type: {file.content_type}")
            # Don't reject based on MIME type alone, extension check is primary
        
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE / 1024 / 1024:.2f}MB)"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Reset file pointer for parsing
        from io import BytesIO
        file.file = BytesIO(file_content)
        
        # 1. Parse document
        content = await parse_document(file)
        
        if not content or len(content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Document appears to be empty or could not be parsed"
            )
        
        # 2. Chunk text
        chunks = chunk_text(content, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_CHUNK_OVERLAP)
        
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
        logger.error(f"Error processing document {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing document. Please try again.")

