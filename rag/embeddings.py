from openai import OpenAI
from typing import List
import os
import asyncio

# Initialize OpenAI client (lazy loading)
_client = None

def _get_client():
    """Lazy load the OpenAI client"""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI API"""
    
    if not texts:
        return []
    
    try:
        client = _get_client()
        
        # Run synchronous OpenAI call in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _create_embeddings():
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]
        
        # Execute in thread pool
        embeddings = await loop.run_in_executor(None, _create_embeddings)
        return embeddings
    
    except Exception as e:
        raise Exception(f"Error generating embeddings: {str(e)}")

