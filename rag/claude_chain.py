from anthropic import Anthropic
import os
import asyncio
import logging
from typing import List, Dict, Any
from config import ANTHROPIC_TIMEOUT, API_MAX_RETRIES
from lib.retry import retry_with_backoff

logger = logging.getLogger(__name__)

# Lazy client initialization
_client = None

def get_client():
    """Get or create Anthropic client"""
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        # Temporarily unset proxy environment variables to prevent Anthropic/httpx from using them
        # Anthropic 0.39.0 doesn't support 'proxies' parameter in constructor
        # httpx (used by Anthropic) auto-detects proxies from env vars, which causes issues
        original_proxies = {}
        proxy_vars = [
            'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
            'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy'
        ]
        
        for var in proxy_vars:
            if var in os.environ:
                original_proxies[var] = os.environ.pop(var)
                logger.debug(f"Temporarily unset {var} to prevent proxy issues")
        
        try:
            # Only pass api_key - Anthropic 0.39.0 doesn't support timeout or proxies in constructor
            # Timeout is handled via asyncio.wait_for in _call_claude()
            _client = Anthropic(api_key=api_key)
            logger.info("Anthropic client initialized successfully (proxies disabled)")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
        finally:
            # Restore proxy environment variables if they were set
            for var, value in original_proxies.items():
                os.environ[var] = value
                logger.debug(f"Restored {var}")
    return _client

async def generate_response(
    query: str, 
    context: List[Dict[str, Any]], 
    conversation_id: str = None
) -> Dict[str, Any]:
    """Generate response using Claude with RAG context"""
    
    if not context:
        return {
            "answer": "I don't have any relevant context to answer your question. Please upload some documents first.",
            "sources": [],
            "conversation_id": conversation_id or "new"
        }
    
    # Build context from retrieved chunks
    context_text = "\n\n".join([
        f"[Source {i+1}: {chunk.get('metadata', {}).get('filename', 'Unknown')}]\n{chunk.get('text', '')}"
        for i, chunk in enumerate(context)
    ])
    
    # Prompt for Claude
    prompt = f"""You are a helpful AI assistant answering questions based on provided documents.

Context from documents:
{context_text}

User question: {query}

Instructions:
1. Answer based ONLY on the provided context
2. If the answer isn't in the context, say so clearly
3. Cite sources using [Source N] notation
4. Be concise but comprehensive
5. If multiple sources support your answer, mention all
6. If the context doesn't contain enough information, acknowledge this honestly

Answer:"""
    
    async def _call_claude():
        """Call Claude API with timeout"""
        client = get_client()
        loop = asyncio.get_event_loop()
        
        def _sync_create():
            try:
                return client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            except Exception as e:
                logger.error(f"Anthropic API error: {str(e)}")
                raise
        
        try:
            message = await asyncio.wait_for(
                loop.run_in_executor(None, _sync_create),
                timeout=ANTHROPIC_TIMEOUT
            )
            return message
        except asyncio.TimeoutError:
            logger.error(f"Anthropic API timeout after {ANTHROPIC_TIMEOUT} seconds")
            raise Exception(f"Anthropic API request timed out after {ANTHROPIC_TIMEOUT} seconds")
    
    try:
        # Call Claude API with retry logic
        message = await retry_with_backoff(
            _call_claude,
            max_retries=API_MAX_RETRIES,
            exceptions=(Exception,)
        )
        
        answer = message.content[0].text
        
        # Extract sources
        sources = [
            {
                "filename": chunk.get("metadata", {}).get("filename", "Unknown"),
                "text": chunk.get("text", "")[:200] + "..." if len(chunk.get("text", "")) > 200 else chunk.get("text", ""),
                "chunk_id": chunk.get("metadata", {}).get("chunk_id", None)
            }
            for chunk in context
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "conversation_id": conversation_id or "new"
        }
        
    except Exception as e:
        logger.error(f"Failed to call Claude API after retries: {str(e)}")
        raise Exception(f"Error calling Claude API: {str(e)}")

