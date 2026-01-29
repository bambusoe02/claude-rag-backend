from openai import OpenAI
from typing import List
import os
import asyncio

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI API"""
    
    if not texts:
        return []
    
    if not client.api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    try:
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

