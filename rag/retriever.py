from rag.embeddings import get_embeddings
from rag.chroma_client import get_chroma_collection
from typing import List, Dict, Any

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

async def retrieve_relevant_chunks(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve most relevant chunks for query"""
    
    if not query or not query.strip():
        return []
    
    try:
        # Generate query embedding
        query_embeddings = await get_embeddings([query])
        
        if not query_embeddings:
            return []
        
        query_embedding = query_embeddings[0]
        
        # Search in ChromaDB
        collection = get_chroma_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, 10)  # Limit to 10 max
        )
        
        # Format results
        chunks = []
        if results['documents'] and len(results['documents']) > 0:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            for i, doc_text in enumerate(documents):
                chunk = {
                    "text": doc_text,
                    "metadata": metadatas[i] if i < len(metadatas) else {}
                }
                chunks.append(chunk)
        
        return chunks
        
    except Exception as e:
        # Log error but return empty list to prevent breaking the API
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error retrieving chunks: {str(e)}", exc_info=True)
        return []

