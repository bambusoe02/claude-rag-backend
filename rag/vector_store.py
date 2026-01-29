from typing import List, Dict, Any
from rag.chroma_client import get_chroma_collection

async def store_documents(
    doc_id: str, 
    chunks: List[str], 
    embeddings: List[List[float]], 
    metadata: Dict[str, Any]
) -> None:
    """Store document chunks in ChromaDB"""
    
    if not chunks or not embeddings:
        raise ValueError("Chunks and embeddings cannot be empty")
    
    if len(chunks) != len(embeddings):
        raise ValueError("Number of chunks must match number of embeddings")
    
    # Prepare IDs, documents, embeddings, and metadatas
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {**metadata, "chunk_id": i, "doc_id": doc_id}
        for i in range(len(chunks))
    ]
    
    # Add to collection
    collection = get_chroma_collection()
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

