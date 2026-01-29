from typing import List, Dict, Any
from rag.chroma_client import get_chroma_collection
import logging

logger = logging.getLogger(__name__)

async def store_documents(
    doc_id: str, 
    chunks: List[str], 
    embeddings: List[List[float]], 
    metadata: Dict[str, Any]
) -> None:
    """Store document chunks in ChromaDB"""
    
    logger.info(f"[VECTOR_STORE] Storing {len(chunks)} chunks for doc_id: {doc_id}")
    
    if not chunks or not embeddings:
        logger.error("[VECTOR_STORE] Chunks or embeddings are empty")
        raise ValueError("Chunks and embeddings cannot be empty")
    
    if len(chunks) != len(embeddings):
        logger.error(f"[VECTOR_STORE] Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")
        raise ValueError("Number of chunks must match number of embeddings")
    
    # Prepare IDs, documents, embeddings, and metadatas
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {**metadata, "chunk_id": i, "doc_id": doc_id}
        for i in range(len(chunks))
    ]
    
    logger.info(f"[VECTOR_STORE] Prepared {len(ids)} IDs for storage")
    
    # Add to collection
    collection = get_chroma_collection()
    try:
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"[VECTOR_STORE] Successfully stored {len(chunks)} chunks")
        
        # Verify stored
        count = collection.count()
        logger.info(f"[VECTOR_STORE] Total documents in collection: {count}")
    except Exception as e:
        logger.error(f"[VECTOR_STORE] Error storing documents: {str(e)}", exc_info=True)
        raise

