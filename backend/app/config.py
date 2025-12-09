import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "Book RAG Chatbot"
    environment: str = "development"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Qdrant
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str = "book_chunks"
    
    # Neon Postgres
    database_url: str
    
    # Retrieval
    top_k: int = 5
    score_threshold: float = 0.1  # Very low to ensure we get results from vector search
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Rate limiting
    rate_limit_per_minute: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
