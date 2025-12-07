"""Retrieve endpoint for RAG chatbot."""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging

from app.services.retrieval import retrieval_service
from app.models.document import QdrantSearchResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["retrieval"])


class RetrieveRequest(BaseModel):
    """Request model for retrieve endpoint."""
    
    question: str = Field(..., min_length=1, description="User question")
    top_k: int = Field(10, ge=1, le=50, description="Number of chunks to retrieve")
    module_filter: Optional[str] = Field(None, description="Filter by module (e.g., module-01-ros2)")
    lang: str = Field("en", description="Language filter (en or ur)")


class ChunkResponse(BaseModel):
    """Response model for a single chunk."""
    
    chunk_id: str
    content: str
    chapter_id: str
    section: str
    heading_path: list
    file_url: str
    score: float


class RetrieveResponse(BaseModel):
    """Response model for retrieve endpoint."""
    
    chunks: List[ChunkResponse]
    total: int


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_chunks(request: RetrieveRequest):
    """Retrieve relevant chunks for a question.
    
    This endpoint returns the most relevant document chunks for a given question
    without generating an answer. Useful for debugging or custom LLM pipelines.
    
    Args:
        request: Retrieve request with question and filters
        
    Returns:
        List of relevant chunks with scores
        
    Raises:
        HTTPException: 500 if retrieval fails
    """
    try:
        logger.info(f"Retrieve request: {request.question[:100]}... (top_k={request.top_k})")
        
        # Retrieve chunks
        results = await retrieval_service.retrieve_chunks(
            question=request.question,
            top_k=request.top_k,
            module_filter=request.module_filter,
            lang=request.lang,
            scope="fullbook"
        )
        
        # Format response
        chunks = [
            ChunkResponse(
                chunk_id=r.chunk.chunk_id,
                content=r.chunk.content,
                chapter_id=r.chunk.chapter_id,
                section=r.chunk.section,
                heading_path=r.chunk.heading_path,
                file_url=r.chunk.file_url,
                score=r.score
            )
            for r in results
        ]
        
        logger.info(f"Retrieved {len(chunks)} chunks")
        
        return RetrieveResponse(
            chunks=chunks,
            total=len(chunks)
        )
        
    except Exception as e:
        logger.error(f"Retrieve endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)}"
        )
