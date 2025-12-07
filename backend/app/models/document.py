"""Document chunk Pydantic models for vector storage."""

from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


class DocumentChunk(BaseModel):
    """A chunk of textbook content with metadata and embedding."""
    
    # Primary identifier
    chunk_id: str = Field(description="UUID v4 for chunk")
    
    # Content
    content: str = Field(description="Raw text content (400-800 tokens)")
    embedding: List[float] = Field(description="1536-dim vector from text-embedding-3-small")
    
    # Hierarchy metadata
    chapter_id: str = Field(description="e.g., 'module-01-ros2/02-nodes-topics-services'")
    module: str = Field(description="e.g., 'module-01-ros2'")
    section: str = Field(description="Section heading, e.g., 'Publisher/Subscriber Pattern'")
    heading_path: str = Field(description="Full breadcrumb, e.g., 'Module 1 > ROS 2 > Publisher/Subscriber'")
    
    # URLs and references
    file_url: str = Field(description="Docusaurus URL path, e.g., '/docs/module-01-ros2/02-nodes-topics-services'")
    source_file: str = Field(description="Original markdown file path")
    
    # Content classification
    chunk_type: Literal["content", "code", "exercise"] = Field(description="Type of content")
    lang: Literal["en", "ur"] = Field(default="en", description="Language")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords for filtering")
    
    # Indexing metadata
    indexed_at: str = Field(description="ISO 8601 timestamp of indexing")
    chunk_index: int = Field(description="Position in source document (0-indexed)")
    total_chunks: int = Field(description="Total chunks from source document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "a7f3c8d2-4e1b-4f9a-8c3d-2e5f6a7b8c9d",
                "content": "In ROS 2, a publisher is a node that sends messages to a topic...",
                "embedding": [0.023, -0.145, 0.389],
                "chapter_id": "module-01-ros2/02-nodes-topics-services",
                "module": "module-01-ros2",
                "section": "Publisher Pattern",
                "heading_path": "Module 1: ROS 2 > Nodes, Topics, Services > Publisher Pattern",
                "file_url": "/docs/module-01-ros2/02-nodes-topics-services#publisher-pattern",
                "source_file": "frontend/docs/module-01-ros2/02-nodes-topics-services.md",
                "chunk_type": "content",
                "lang": "en",
                "keywords": ["publisher", "rclpy", "topic"],
                "indexed_at": "2025-12-06T10:30:00Z",
                "chunk_index": 0,
                "total_chunks": 5
            }
        }


class QdrantSearchResult(BaseModel):
    """Search result from Qdrant."""
    
    chunk: DocumentChunk
    score: float = Field(description="Similarity score (0-1)")
    
    
class ChunkMetadata(BaseModel):
    """Metadata for a document chunk (without embedding)."""
    
    chunk_id: str
    chapter_id: str
    module: str
    section: str
    heading_path: str
    file_url: str
    chunk_type: Literal["content", "code", "exercise"]
    lang: Literal["en", "ur"]
    keywords: List[str]
