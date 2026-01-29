from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
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
limiter = Limiter(key_func=get_remote_address)

@router.post("/document")
@limiter.limit("5/minute")
async def upload_document(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and process document for RAG"""
    
    logger.info(f"[UPLOAD] Received upload request for file: {file.filename}")
    logger.info(f"[UPLOAD] Content type: {file.content_type}")
    logger.info(f"[UPLOAD] Request origin: {request.headers.get('origin', 'unknown')}")
    
    try:
        # Validate file extension
        if not file.filename:
            logger.error("[UPLOAD] Filename is missing")
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
        logger.info(f"[UPLOAD] File size: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
        
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
        logger.info("[UPLOAD] Parsing document...")
        content = await parse_document(file)
        logger.info(f"[UPLOAD] Parsed content length: {len(content)} characters")
        
        if not content or len(content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Document appears to be empty or could not be parsed"
            )
        
        # 2. Chunk text
        logger.info("[UPLOAD] Chunking text...")
        chunks = chunk_text(content, chunk_size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_CHUNK_OVERLAP)
        logger.info(f"[UPLOAD] Created {len(chunks)} chunks")
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks generated from document"
            )
        
        # 3. Generate embeddings
        logger.info("[UPLOAD] Generating embeddings...")
        embeddings = await get_embeddings(chunks)
        logger.info(f"[UPLOAD] Generated {len(embeddings)} embeddings")
        
        # 4. Store in vector DB
        doc_id = str(uuid.uuid4())
        logger.info(f"[UPLOAD] Storing document with ID: {doc_id}")
        await store_documents(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata={"filename": file.filename, "file_type": file.content_type}
        )
        logger.info(f"[UPLOAD] Document stored successfully. Returning response.")
        
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
        error_msg = str(e)
        logger.error(f"Error processing document {file.filename}: {error_msg}", exc_info=True)
        # Include more detail in error message for debugging
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {error_msg}")

