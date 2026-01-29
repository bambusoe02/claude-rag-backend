from sentence_transformers import SentenceTransformer
from typing import List
import asyncio

# Initialize model (lazy loading)
_model = None

def _get_model():
    """Lazy load the embedding model"""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for text chunks"""
    
    if not texts:
        return []
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    model = _get_model()
    
    # Generate embeddings
    embeddings = await loop.run_in_executor(
        None,
        lambda: model.encode(texts, show_progress_bar=False)
    )
    
    return embeddings.tolist()

