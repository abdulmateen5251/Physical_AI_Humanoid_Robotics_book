"""Feedback endpoint for RAG chatbot."""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.services.database import Database, get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """Request model for feedback endpoint."""
    
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    question: str = Field(..., min_length=1, description="Original question")
    answer: str = Field(..., min_length=1, description="Generated answer")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 (1=poor, 5=excellent)")
    chunk_ids: List[str] = Field(default_factory=list, description="Retrieved chunk IDs")
    scope: str = Field("fullbook", description="Query scope")
    comment: Optional[str] = Field(None, description="Optional user comment")
    user_id: Optional[str] = Field(None, description="User ID")


class FeedbackResponse(BaseModel):
    """Response model for feedback endpoint."""
    
    success: bool
    feedback_id: Optional[int] = None
    message: str


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: Database = Depends(get_db)
):
    """Submit feedback for a Q&A interaction.
    
    This endpoint stores user feedback to improve the RAG system.
    Feedback includes:
    - Rating (1-5)
    - Optional comment
    - Q&A context (question, answer, chunks used)
    
    Args:
        request: Feedback request with rating and context
        db: Database connection
        
    Returns:
        Feedback submission result
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        logger.info(f"Feedback submission: rating={request.rating}, scope={request.scope}")
        
        # Insert feedback into database
        query = """
            INSERT INTO answer_sessions (
                session_id, user_id, question, answer, scope,
                chunk_ids, rating, comment, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
        """
        
        feedback_id = await db.pool.fetchval(
            query,
            request.session_id,
            request.user_id,
            request.question,
            request.answer,
            request.scope,
            request.chunk_ids,
            request.rating,
            request.comment,
            datetime.utcnow()
        )
        
        logger.info(f"Feedback stored: id={feedback_id}")
        
        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message="Feedback submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Feedback endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback submission failed: {str(e)}"
        )


@router.get("/feedback/stats")
async def get_feedback_stats(db: Database = Depends(get_db)):
    """Get feedback statistics.
    
    Returns aggregate statistics about user feedback for monitoring
    system performance and user satisfaction.
    
    Args:
        db: Database connection
        
    Returns:
        Feedback statistics
    """
    try:
        query = """
            SELECT 
                COUNT(*) as total_feedback,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_count,
                COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_count,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM answer_sessions
            WHERE created_at > NOW() - INTERVAL '30 days'
        """
        
        stats = await db.pool.fetchrow(query)
        
        return {
            "total_feedback": stats["total_feedback"],
            "avg_rating": float(stats["avg_rating"]) if stats["avg_rating"] else 0.0,
            "positive_count": stats["positive_count"],
            "negative_count": stats["negative_count"],
            "unique_sessions": stats["unique_sessions"]
        }
        
    except Exception as e:
        logger.error(f"Feedback stats failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback stats: {str(e)}"
        )
