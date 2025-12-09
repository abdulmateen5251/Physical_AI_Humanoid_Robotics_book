from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import get_settings
from typing import List, Dict, Optional
import uuid

settings = get_settings()

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = settings.qdrant_collection
    
    def create_collection(self, vector_size: int = 1536):
        """Create collection if not exists"""
        try:
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
    
    def upsert_chunks(self, chunks: List[Dict]):
        """Upsert chunks with embeddings and metadata"""
        points = []
        for chunk in chunks:
            point = PointStruct(
                id=chunk.get("chunk_id", str(uuid.uuid4())),
                vector=chunk["embedding"],
                payload={
                    "text": chunk["text"],
                    "chapter": chunk.get("chapter"),
                    "section": chunk.get("section"),
                    "page": chunk.get("page"),
                    "uri": chunk.get("uri"),
                    "char_start": chunk.get("char_start"),
                    "char_end": chunk.get("char_end"),
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 5,
        score_threshold: float = 0.3,
        chapter: Optional[str] = None,
        section: Optional[str] = None,
        page: Optional[str] = None
    ):
        """Search with vector similarity - Qdrant Cloud compatible"""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        filter_conditions = []
        
        if chapter:
            filter_conditions.append(
                FieldCondition(key="chapter", match=MatchValue(value=chapter))
            )
        if section:
            filter_conditions.append(
                FieldCondition(key="section", match=MatchValue(value=section))
            )
        if page:
            filter_conditions.append(
                FieldCondition(key="page", match=MatchValue(value=page))
            )
        
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Qdrant Cloud uses .query_points() with query parameter
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=search_filter
        )
        
        # Extract points from response
        results = response.points if hasattr(response, 'points') else response
        
        return [
            {
                "chunk_id": str(result.id),
                "text": result.payload.get("text", ""),
                "score": result.score,
                "chapter": result.payload.get("chapter"),
                "section": result.payload.get("section"),
                "page": result.payload.get("page"),
                "uri": result.payload.get("uri"),
                "char_start": result.payload.get("char_start"),
                "char_end": result.payload.get("char_end"),
            }
            for result in results
        ]

qdrant_service = QdrantService()
