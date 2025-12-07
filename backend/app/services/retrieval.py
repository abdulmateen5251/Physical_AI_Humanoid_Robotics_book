"""Retrieval service for RAG chatbot."""

from typing import List, Optional, Dict, Any
import logging

from app.models.document import DocumentChunk, QdrantSearchResult
from app.services.qdrant_client import qdrant_service
from app.utils.embeddings import generate_embedding
from app.config import settings

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving relevant document chunks."""
    
    def __init__(self):
        """Initialize retrieval service."""
        self.qdrant = qdrant_service
        self.top_k = settings.max_retrieval_chunks
    
    async def retrieve_chunks(
        self,
        question: str,
        top_k: Optional[int] = None,
        module_filter: Optional[str] = None,
        lang: str = "en",
        scope: str = "fullbook"
    ) -> List[QdrantSearchResult]:
        """Retrieve relevant chunks for a question.
        
        Args:
            question: User question
            top_k: Number of results to return (default: from settings)
            module_filter: Filter by module (e.g., "module-01-ros2")
            lang: Language filter
            scope: Query scope ("fullbook" or "selected_text")
            
        Returns:
            List of QdrantSearchResult with chunks and scores
        """
        if top_k is None:
            top_k = self.top_k
        
        try:
            # Generate query embedding
            logger.info(f"Generating embedding for question: {question[:100]}...")
            query_vector = await generate_embedding(question)
            
            # Search Qdrant
            logger.info(f"Searching Qdrant (top_k={top_k}, module={module_filter})")
            results = self.qdrant.search(
                query_vector=query_vector,
                top_k=top_k,
                module_filter=module_filter,
                lang_filter=lang,
                chunk_type_filter=None  # Include all chunk types
            )
            
            logger.info(f"Retrieved {len(results)} chunks")
            
            # Log relevance scores
            if results:
                scores = [r.score for r in results]
                logger.info(f"Relevance scores: min={min(scores):.3f}, max={max(scores):.3f}, avg={sum(scores)/len(scores):.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}", exc_info=True)
            raise
    
    def format_context_for_llm(
        self,
        results: List[QdrantSearchResult],
        max_context_length: int = 8000
    ) -> str:
        """Format retrieved chunks as context for LLM.
        
        Args:
            results: Retrieved search results
            max_context_length: Maximum context length in characters
            
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results):
            chunk = result.chunk
            score = result.score
            
            # Format chunk with metadata
            chunk_text = f"""
Source {i+1} (Score: {score:.3f}):
Chapter: {chunk.chapter_id}
Section: {chunk.section}
URL: {chunk.file_url}

{chunk.content}

---
"""
            
            # Check if adding this chunk would exceed max length
            if current_length + len(chunk_text) > max_context_length:
                logger.warning(f"Context length limit reached. Including {i}/{len(results)} chunks.")
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        formatted_context = "\n".join(context_parts)
        logger.info(f"Formatted context: {current_length} chars from {len(context_parts)} chunks")
        
        return formatted_context
    
    def get_source_citations(self, results: List[QdrantSearchResult]) -> List[Dict[str, Any]]:
        """Extract source citations from results.
        
        Args:
            results: Retrieved search results
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        for result in results:
            chunk = result.chunk
            citations.append({
                "chapter_id": chunk.chapter_id,
                "section": chunk.section,
                "file_url": chunk.file_url,
                "heading_path": chunk.heading_path,
                "score": result.score
            })
        
        return citations


# Global retrieval service instance
retrieval_service = RetrievalService()
