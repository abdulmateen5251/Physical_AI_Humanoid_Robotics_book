"""RAG agent orchestration."""

from typing import Optional, Dict, Any, List
import logging
import time

from app.services.retrieval import retrieval_service
from app.services.llm import llm_service
from app.models.document import QdrantSearchResult

logger = logging.getLogger(__name__)


class RAGAgent:
    """RAG agent for orchestrating retrieval and answer generation."""
    
    def __init__(self):
        """Initialize RAG agent."""
        self.retrieval = retrieval_service
        self.llm = llm_service
    
    async def answer_question(
        self,
        question: str,
        scope: str = "fullbook",
        selected_text: Optional[str] = None,
        module_filter: Optional[str] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Answer a question using RAG pipeline.
        
        Args:
            question: User question
            scope: Query scope ("fullbook" or "selected_text")
            selected_text: Selected text (for selection mode)
            module_filter: Filter by module
            top_k: Number of chunks to retrieve
            
        Returns:
            Answer dictionary with response and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant chunks (skip for selection mode)
            if scope == "fullbook":
                logger.info(f"Starting RAG pipeline (scope: {scope})")
                
                # Retrieve chunks
                results = await self.retrieval.retrieve_chunks(
                    question=question,
                    top_k=top_k,
                    module_filter=module_filter,
                    scope=scope
                )
                
                if not results:
                    logger.warning("No relevant chunks found")
                    return {
                        "answer": "I don't have enough information in the textbook to answer this question.",
                        "sources": [],
                        "chunk_ids": [],
                        "retrieval_score_avg": 0.0,
                        "response_time_ms": int((time.time() - start_time) * 1000)
                    }
                
                # Format context for LLM
                context = self.retrieval.format_context_for_llm(results)
                
                # Get citations
                citations = self.retrieval.get_source_citations(results)
                chunk_ids = [r.chunk.chunk_id for r in results]
                
                # Calculate average retrieval score
                avg_score = sum(r.score for r in results) / len(results)
                
            else:
                # Selection mode: use selected text as context
                logger.info(f"Starting selection mode pipeline")
                
                if not selected_text:
                    raise ValueError("selected_text required for selection mode")
                
                context = selected_text
                citations = []
                chunk_ids = []
                avg_score = 1.0
            
            # Step 2: Generate answer with LLM
            answer = await self.llm.generate_answer(
                question=question,
                context=context,
                scope=scope,
                selected_text=selected_text
            )
            
            # Step 3: Validate answer quality (for fullbook mode)
            if scope == "fullbook":
                quality_metrics = await self.llm.validate_answer_quality(
                    question=question,
                    answer=answer,
                    context=context
                )
                logger.info(f"Answer quality: {quality_metrics}")
            
            response_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"RAG pipeline complete in {response_time}ms")
            
            return {
                "answer": answer,
                "sources": citations,
                "chunk_ids": chunk_ids,
                "retrieval_score_avg": avg_score,
                "response_time_ms": response_time,
                "scope": scope
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}", exc_info=True)
            raise


# Global RAG agent instance
rag_agent = RAGAgent()
