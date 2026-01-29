from anthropic import Anthropic
import os
from typing import List, Dict, Any

# Lazy client initialization
_client = None

def get_client():
    """Get or create Anthropic client"""
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        _client = Anthropic(api_key=api_key)
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
    
    try:
        # Call Claude API
        client = get_client()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
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
        raise Exception(f"Error calling Claude API: {str(e)}")

