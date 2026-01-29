from openai import OpenAI
from typing import List
import os
import asyncio
import logging
from config import OPENAI_TIMEOUT, API_MAX_RETRIES
from lib.retry import retry_with_backoff

logger = logging.getLogger(__name__)

# Initialize OpenAI client (lazy loading)
_client = None

def _get_client():
    """Lazy load the OpenAI client"""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key, timeout=OPENAI_TIMEOUT)
    return _client

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI API with retry logic"""
    
    if not texts:
        return []
    
    async def _create_embeddings():
        client = _get_client()
        loop = asyncio.get_event_loop()
        
        def _sync_create():
            try:
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
                raise
        
        # Execute in thread pool with timeout
        try:
            embeddings = await asyncio.wait_for(
                loop.run_in_executor(None, _sync_create),
                timeout=OPENAI_TIMEOUT
            )
            return embeddings
        except asyncio.TimeoutError:
            logger.error(f"OpenAI API timeout after {OPENAI_TIMEOUT} seconds")
            raise Exception(f"OpenAI API request timed out after {OPENAI_TIMEOUT} seconds")
    
    try:
        return await retry_with_backoff(
            _create_embeddings,
            max_retries=API_MAX_RETRIES,
            exceptions=(Exception,)
        )
    except Exception as e:
        logger.error(f"Failed to generate embeddings after retries: {str(e)}")
        raise Exception(f"Error generating embeddings: {str(e)}")

