"""AnswerSession and Translation Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime


class AnswerSession(BaseModel):
    """Answer session model for tracking user interactions."""
    
    session_id: str = Field(description="UUID v4")
    user_id: Optional[str] = Field(default=None, description="User ID if authenticated")
    
    # Question and answer
    question: str = Field(description="User question")
    answer: str = Field(description="Generated answer")
    
    # RAG metadata
    scope: Literal["fullbook", "selected_text"] = Field(description="Query scope")
    selected_text: Optional[str] = Field(default=None, description="Selected text if scope=selected_text")
    chunk_ids: List[str] = Field(default_factory=list, description="IDs of retrieved chunks")
    
    # Quality metrics
    retrieval_score_avg: Optional[float] = Field(default=None, description="Average relevance score")
    llm_model: str = Field(description="LLM model used (e.g., gpt-4o)")
    
    # User feedback
    feedback_rating: Optional[int] = Field(default=None, ge=1, le=5, description="User rating 1-5")
    feedback_comment: Optional[str] = Field(default=None, description="User feedback text")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[int] = Field(default=None, description="Response generation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "750e8400-e29b-41d4-a716-446655440002",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "question": "How do I create a publisher in rclpy?",
                "answer": "To create a publisher in rclpy, use the create_publisher() method...",
                "scope": "fullbook",
                "selected_text": None,
                "chunk_ids": ["a7f3c8d2-4e1b-4f9a-8c3d-2e5f6a7b8c9d"],
                "retrieval_score_avg": 0.89,
                "llm_model": "gpt-4o",
                "feedback_rating": 5,
                "feedback_comment": "Very helpful!",
                "created_at": "2025-12-06T10:45:00Z",
                "response_time_ms": 2500
            }
        }


class PersonalizedContent(BaseModel):
    """Personalized content cache model."""
    
    content_id: str = Field(description="UUID v4")
    user_id: str = Field(description="User ID")
    chapter_id: str = Field(description="Chapter identifier")
    
    # Personalization parameters (cache key components)
    background: str
    difficulty_level: str
    examples_preference: str
    
    # Content
    original_content: str = Field(description="Original chapter content")
    personalized_content: str = Field(description="Personalized content")
    
    # Metadata
    llm_model: str = Field(description="Model used for personalization")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(description="Cache expiration (24h TTL)")
