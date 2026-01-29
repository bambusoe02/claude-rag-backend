from typing import List
import os
import asyncio
import logging
from config import ANTHROPIC_TIMEOUT, API_MAX_RETRIES
from lib.retry import retry_with_backoff

logger = logging.getLogger(__name__)

# Try to use OpenAI if available, otherwise use sentence-transformers (local, free)
_embedding_model = None
_use_openai = None

def _get_embedding_model():
    """Get embedding model - prefer OpenAI, fallback to sentence-transformers"""
    global _embedding_model, _use_openai
    
    if _embedding_model is not None:
        return _embedding_model, _use_openai
    
    # Check if OpenAI API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            from config import OPENAI_TIMEOUT
            _embedding_model = OpenAI(api_key=openai_key, timeout=OPENAI_TIMEOUT)
            _use_openai = True
            logger.info("Using OpenAI embeddings API")
            return _embedding_model, _use_openai
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")
    
    # Fallback to sentence-transformers (local, free, no API key needed)
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Initializing sentence-transformers model (this may take a moment on first run)...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        _use_openai = False
        logger.info("✅ Using sentence-transformers (local embeddings, no API key required)")
        return _embedding_model, _use_openai
    except ImportError as e:
        logger.error(f"sentence-transformers not installed: {e}")
        logger.error("Install with: pip install sentence-transformers")
        raise ValueError("No embedding model available. Either set OPENAI_API_KEY or install sentence-transformers")
    except Exception as e:
        logger.error(f"Failed to initialize sentence-transformers: {e}", exc_info=True)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI API or sentence-transformers"""
    
    if not texts:
        return []
    
    async def _create_embeddings():
        model, use_openai = _get_embedding_model()
        loop = asyncio.get_event_loop()
        
        def _sync_create():
            try:
                if use_openai:
                    # Use OpenAI API
                    response = model.embeddings.create(
                        model="text-embedding-3-small",
                        input=texts
                    )
                    return [item.embedding for item in response.data]
                else:
                    # Use sentence-transformers (local)
                    logger.debug(f"Generating embeddings for {len(texts)} texts using sentence-transformers")
                    embeddings = model.encode(texts, convert_to_numpy=False, show_progress_bar=False)
                    # Convert to list of lists
                    result = [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings]
                    logger.debug(f"Generated {len(result)} embeddings, dimension: {len(result[0]) if result else 0}")
                    return result
            except Exception as e:
                logger.error(f"Embedding generation error: {str(e)}")
                raise
        
        # Execute in thread pool with timeout
        try:
            embeddings = await asyncio.wait_for(
                loop.run_in_executor(None, _sync_create),
                timeout=ANTHROPIC_TIMEOUT
            )
            return embeddings
        except asyncio.TimeoutError:
            logger.error(f"Embedding generation timeout after {ANTHROPIC_TIMEOUT} seconds")
            raise Exception(f"Embedding generation timed out after {ANTHROPIC_TIMEOUT} seconds")
    
    try:
        return await retry_with_backoff(
            _create_embeddings,
            max_retries=API_MAX_RETRIES,
            exceptions=(Exception,)
        )
    except Exception as e:
        logger.error(f"Failed to generate embeddings after retries: {str(e)}")
        raise Exception(f"Error generating embeddings: {str(e)}")

