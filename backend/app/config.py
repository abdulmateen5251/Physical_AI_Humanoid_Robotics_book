"""Application configuration using Pydantic Settings."""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    
    # OpenAI
    openai_api_key: str = Field(default="", description="OpenAI API key")
    
    # Anthropic
    anthropic_api_key: str = Field(default="", description="Anthropic API key for Claude")
    
    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant cluster URL")
    qdrant_api_key: str = Field(default="", description="Qdrant API key")
    qdrant_collection: str = Field(default="physical_ai_humanoid_robotics_course")
    
    # Database
    database_url: str = Field(default="postgresql+asyncpg://user:password@localhost:5432/textbook", description="PostgreSQL connection string")
    
    # Authentication
    better_auth_client_id: str = Field(default="")
    better_auth_client_secret: str = Field(default="")
    jwt_secret_key: str = Field(default="dev-secret-key-change-in-production-at-least-32-chars", description="JWT signing key")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_minutes: int = Field(default=1440)  # 24 hours
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [origin.strip() for origin in self.cors_origins.split(',')]
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60)
    
    # RAG Settings
    embedding_model: str = Field(default="text-embedding-3-small")
    llm_model: str = Field(default="gpt-4o")
    max_retrieval_chunks: int = Field(default=10)
    chunk_size_min: int = Field(default=400)
    chunk_size_max: int = Field(default=800)
    
    # Personalization
    personalization_cache_ttl: int = Field(default=86400)  # 24 hours in seconds
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance with error handling
try:
    settings = Settings()
except Exception as e:
    import warnings
    warnings.warn(f"Failed to load settings: {e}. Using defaults.")
    settings = Settings(_env_file=None)
