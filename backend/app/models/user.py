"""User and UserProfile Pydantic models."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime


class User(BaseModel):
    """User model matching Postgres schema."""
    
    user_id: str = Field(description="UUID v4")
    email: EmailStr = Field(description="User email address")
    password_hash: str = Field(description="Bcrypt hashed password")
    name: str = Field(description="User display name")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "student@example.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU2JQVY.AHGm",
                "name": "Ahmed Khan",
                "created_at": "2025-12-06T10:00:00Z",
                "last_login": "2025-12-06T10:30:00Z",
                "is_active": True
            }
        }


class UserProfile(BaseModel):
    """User profile model for personalization."""
    
    profile_id: str = Field(description="UUID v4")
    user_id: str = Field(description="Foreign key to users")
    
    # Personalization preferences
    background: Literal["software", "hardware", "beginner", "researcher"] = Field(
        default="beginner",
        description="User technical background"
    )
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(
        default="beginner",
        description="Preferred difficulty level"
    )
    examples_preference: Literal["minimal", "moderate", "extensive"] = Field(
        default="moderate",
        description="Number of code examples preferred"
    )
    
    # Language preferences
    preferred_language: Literal["en", "ur"] = Field(default="en")
    
    # Consent flags
    consent_personalization: bool = Field(default=False)
    consent_data_collection: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile_id": "650e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "background": "software",
                "difficulty_level": "intermediate",
                "examples_preference": "extensive",
                "preferred_language": "en",
                "consent_personalization": True,
                "consent_data_collection": True,
                "created_at": "2025-12-06T10:00:00Z",
                "updated_at": "2025-12-06T11:00:00Z"
            }
        }


class UserWithProfile(BaseModel):
    """Combined user and profile data."""
    
    user: User
    profile: UserProfile


class UpdateProfileRequest(BaseModel):
    """Request to update user profile."""
    
    background: Optional[Literal["software", "hardware", "beginner", "researcher"]] = None
    difficulty_level: Optional[Literal["beginner", "intermediate", "advanced"]] = None
    examples_preference: Optional[Literal["minimal", "moderate", "extensive"]] = None
    preferred_language: Optional[Literal["en", "ur"]] = None
    consent_personalization: Optional[bool] = None
    consent_data_collection: Optional[bool] = None
