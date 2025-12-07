"""Qdrant vector database client service."""

from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams
)
import logging

from app.config import settings
from app.models.document import DocumentChunk, QdrantSearchResult

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30
        )
        self.collection_name = settings.qdrant_collection
        
    def init_collection(self, recreate: bool = False) -> None:
        """Initialize or recreate the collection.
        
        Args:
            recreate: If True, delete existing collection and create new one
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if collection_exists and recreate:
                logger.info(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # text-embedding-3-small dimension
                        distance=Distance.COSINE
                    )
                )
                
                # Create payload indexes for fast filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="module",
                    field_schema="keyword"
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="lang",
                    field_schema="keyword"
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="chunk_type",
                    field_schema="keyword"
                )
                
                logger.info(f"Collection created successfully: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise
    
    def upsert_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Upsert document chunks to collection.
        
        Args:
            chunks: List of DocumentChunk objects to upsert
        """
        if not chunks:
            logger.warning("No chunks to upsert")
            return
        
        try:
            points = []
            for chunk in chunks:
                # Convert chunk to Qdrant point
                point = PointStruct(
                    id=chunk.chunk_id,
                    vector=chunk.embedding,
                    payload={
                        "content": chunk.content,
                        "chapter_id": chunk.chapter_id,
                        "module": chunk.module,
                        "section": chunk.section,
                        "heading_path": chunk.heading_path,
                        "file_url": chunk.file_url,
                        "source_file": chunk.source_file,
                        "chunk_type": chunk.chunk_type,
                        "lang": chunk.lang,
                        "keywords": chunk.keywords,
                        "indexed_at": chunk.indexed_at,
                        "chunk_index": chunk.chunk_index,
                        "total_chunks": chunk.total_chunks
                    }
                )
                points.append(point)
            
            # Upsert points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Upserted {len(points)} chunks to {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to upsert chunks: {e}")
            raise
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        module_filter: Optional[str] = None,
        lang_filter: str = "en",
        chunk_type_filter: Optional[str] = None
    ) -> List[QdrantSearchResult]:
        """Search for similar chunks.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            module_filter: Filter by module (e.g., "module-01-ros2")
            lang_filter: Filter by language (default: "en")
            chunk_type_filter: Filter by chunk type (content, code, exercise)
            
        Returns:
            List of QdrantSearchResult objects
        """
        try:
            # Build filter conditions
            must_conditions = [
                FieldCondition(
                    key="lang",
                    match=MatchValue(value=lang_filter)
                )
            ]
            
            if module_filter:
                must_conditions.append(
                    FieldCondition(
                        key="module",
                        match=MatchValue(value=module_filter)
                    )
                )
            
            if chunk_type_filter:
                must_conditions.append(
                    FieldCondition(
                        key="chunk_type",
                        match=MatchValue(value=chunk_type_filter)
                    )
                )
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=Filter(must=must_conditions) if must_conditions else None,
                search_params=SearchParams(
                    hnsw_ef=128,  # Higher value = more accurate but slower
                    exact=False
                )
            )
            
            # Convert to QdrantSearchResult objects
            results = []
            for hit in search_result:
                chunk = DocumentChunk(
                    chunk_id=str(hit.id),
                    content=hit.payload["content"],
                    embedding=[],  # Don't return embedding in search results
                    chapter_id=hit.payload["chapter_id"],
                    module=hit.payload["module"],
                    section=hit.payload["section"],
                    heading_path=hit.payload["heading_path"],
                    file_url=hit.payload["file_url"],
                    source_file=hit.payload["source_file"],
                    chunk_type=hit.payload["chunk_type"],
                    lang=hit.payload["lang"],
                    keywords=hit.payload["keywords"],
                    indexed_at=hit.payload["indexed_at"],
                    chunk_index=hit.payload["chunk_index"],
                    total_chunks=hit.payload["total_chunks"]
                )
                
                results.append(QdrantSearchResult(
                    chunk=chunk,
                    score=hit.score
                ))
            
            logger.info(f"Found {len(results)} results for query")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.size,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise


# Global Qdrant service instance
qdrant_service = QdrantService()
