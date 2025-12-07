"""LLM service for answer generation."""

from typing import Optional, AsyncIterator
import logging
from openai import AsyncOpenAI

from app.config import settings
from app.utils.prompts import RAG_SYSTEM_PROMPT, SELECTION_MODE_PROMPT, ERROR_RESPONSE_NO_CONTEXT

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based answer generation."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
    
    async def generate_answer(
        self,
        question: str,
        context: str,
        scope: str = "fullbook",
        selected_text: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Generate answer using LLM.
        
        Args:
            question: User question
            context: Retrieved context or selected text
            scope: Query scope ("fullbook" or "selected_text")
            selected_text: Original selected text (for selection mode)
            stream: Whether to stream the response
            
        Returns:
            Generated answer text
        """
        try:
            # Select appropriate system prompt
            if scope == "selected_text" and selected_text:
                system_prompt = SELECTION_MODE_PROMPT.format(
                    selected_text=selected_text,
                    question=question
                )
                user_message = question
            else:
                system_prompt = RAG_SYSTEM_PROMPT.format(
                    sources=context,
                    question=question
                )
                user_message = question
            
            # Check if context is empty
            if not context.strip():
                logger.warning("Empty context provided")
                return ERROR_RESPONSE_NO_CONTEXT
            
            # Generate answer
            logger.info(f"Generating answer with {self.model} (scope: {scope})")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if stream:
                return await self._generate_streaming(messages)
            else:
                return await self._generate_complete(messages)
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}", exc_info=True)
            raise
    
    async def _generate_complete(self, messages: list) -> str:
        """Generate complete answer (non-streaming).
        
        Args:
            messages: Chat messages
            
        Returns:
            Complete answer text
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,  # Lower temperature for factual accuracy
            max_tokens=1000,
            top_p=0.9
        )
        
        answer = response.choices[0].message.content
        
        # Log usage
        usage = response.usage
        logger.info(
            f"LLM usage: {usage.prompt_tokens} prompt + "
            f"{usage.completion_tokens} completion = {usage.total_tokens} total tokens"
        )
        
        return answer
    
    async def _generate_streaming(self, messages: list) -> AsyncIterator[str]:
        """Generate streaming answer.
        
        Args:
            messages: Chat messages
            
        Yields:
            Answer text chunks
        """
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
            top_p=0.9,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def validate_answer_quality(
        self,
        question: str,
        answer: str,
        context: str
    ) -> dict:
        """Validate answer quality against context.
        
        Args:
            question: Original question
            answer: Generated answer
            context: Retrieved context
            
        Returns:
            Quality metrics dictionary
        """
        # Simple quality checks
        quality_metrics = {
            "has_content": len(answer.strip()) > 0,
            "min_length": len(answer.split()) >= 10,
            "not_error_message": ERROR_RESPONSE_NO_CONTEXT not in answer,
            "question_addressed": any(word.lower() in answer.lower() for word in question.split()[:3])
        }
        
        quality_metrics["is_valid"] = all(quality_metrics.values())
        
        return quality_metrics


# Global LLM service instance
llm_service = LLMService()
