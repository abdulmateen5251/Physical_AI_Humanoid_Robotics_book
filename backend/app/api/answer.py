"""Answer endpoint for RAG chatbot."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging

from app.services.rag_agent import rag_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["answer"])


class AnswerRequest(BaseModel):
    """Request model for answer endpoint."""
    
    question: str = Field(..., min_length=1, description="User question")
    scope: str = Field("fullbook", description="Query scope: 'fullbook' or 'selected_text'")
    selected_text: Optional[str] = Field(None, description="Selected text (required if scope=selected_text)")
    module_filter: Optional[str] = Field(None, description="Filter by module (e.g., module-01-ros2)")
    top_k: int = Field(10, ge=1, le=50, description="Number of chunks to retrieve")
    user_id: Optional[str] = Field(None, description="User ID for personalization")


class SourceCitation(BaseModel):
    """Source citation model."""
    
    chapter_id: str
    section: str
    file_url: str
    heading_path: list
    score: float


class AnswerResponse(BaseModel):
    """Response model for answer endpoint."""
    
    answer: str
    sources: List[SourceCitation]
    chunk_ids: List[str]
    retrieval_score_avg: float
    response_time_ms: int
    scope: str


@router.post("/answer", response_model=AnswerResponse)
async def answer_question(request: AnswerRequest):
    """Answer a question using RAG pipeline.
    
    This is the main RAG endpoint. It:
    1. Retrieves relevant chunks from Qdrant (fullbook mode) or uses selected text
    2. Generates answer using LLM with retrieved context
    3. Returns answer with source citations
    
    Args:
        request: Answer request with question and parameters
        
    Returns:
        Generated answer with sources and metadata
        
    Raises:
        HTTPException: 400 if validation fails, 500 if RAG pipeline fails
    """
    try:
        # Validate scope and selected_text
        if request.scope == "selected_text" and not request.selected_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="selected_text required when scope=selected_text"
            )
        
        logger.info(
            f"Answer request: {request.question[:100]}... "
            f"(scope={request.scope}, module={request.module_filter})"
        )
        
        # Run RAG pipeline
        result = await rag_agent.answer_question(
            question=request.question,
            scope=request.scope,
            selected_text=request.selected_text,
            module_filter=request.module_filter,
            top_k=request.top_k
        )
        
        # Format response
        sources = [
            SourceCitation(
                chapter_id=s["chapter_id"],
                section=s["section"],
                file_url=s["file_url"],
                heading_path=s["heading_path"],
                score=s["score"]
            )
            for s in result["sources"]
        ]
        
        response = AnswerResponse(
            answer=result["answer"],
            sources=sources,
            chunk_ids=result["chunk_ids"],
            retrieval_score_avg=result["retrieval_score_avg"],
            response_time_ms=result["response_time_ms"],
            scope=result["scope"]
        )
        
        logger.info(f"Answer generated in {result['response_time_ms']}ms")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Answer endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Answer generation failed: {str(e)}"
        )
