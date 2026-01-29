from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from rag.retriever import retrieve_relevant_chunks
from rag.claude_chain import generate_response
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's question")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    sources: List[Dict[str, Any]] = Field(..., description="Source documents used")
    conversation_id: str = Field(..., description="Conversation ID")

@router.post("/message", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_message(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """Send message and get RAG-enhanced response"""
    
    try:
        if not chat_request.message or not chat_request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # 1. Retrieve relevant chunks
        relevant_chunks = await retrieve_relevant_chunks(
            query=chat_request.message,
            top_k=5
        )
        
        if not relevant_chunks:
            return ChatResponse(
                response="I don't have any relevant documents in my knowledge base to answer your question. Please upload some documents first.",
                sources=[],
                conversation_id=chat_request.conversation_id or "new"
            )
        
        # 2. Generate response with Claude
        response = await generate_response(
            query=chat_request.message,
            context=relevant_chunks,
            conversation_id=chat_request.conversation_id
        )
        
        return ChatResponse(
            response=response["answer"],
            sources=response["sources"],
            conversation_id=response["conversation_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

