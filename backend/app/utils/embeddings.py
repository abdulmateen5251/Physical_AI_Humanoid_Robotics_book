"""Embedding generation using OpenAI."""

from typing import List
import openai
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = settings.openai_api_key


async def generate_embedding(text: str, model: str = None) -> List[float]:
    """Generate embedding for given text using OpenAI.
    
    Args:
        text: Input text to embed
        model: Embedding model (default: from settings)
        
    Returns:
        1536-dimensional embedding vector
    """
    if model is None:
        model = settings.embedding_model
    
    try:
        # Clean text
        text = text.strip().replace("\n", " ")
        
        if not text:
            raise ValueError("Empty text provided for embedding")
        
        # Generate embedding
        response = openai.embeddings.create(
            input=text,
            model=model
        )
        
        embedding = response.data[0].embedding
        
        logger.debug(f"Generated embedding for text (length: {len(text)})")
        
        return embedding
        
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise


async def generate_embeddings_batch(texts: List[str], model: str = None) -> List[List[float]]:
    """Generate embeddings for multiple texts in batch.
    
    Args:
        texts: List of texts to embed
        model: Embedding model (default: from settings)
        
    Returns:
        List of embedding vectors
    """
    if model is None:
        model = settings.embedding_model
    
    try:
        # Clean texts
        texts = [text.strip().replace("\n", " ") for text in texts]
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t]
        
        if not valid_texts:
            raise ValueError("No valid texts provided for embedding")
        
        # Generate embeddings
        response = openai.embeddings.create(
            input=valid_texts,
            model=model
        )
        
        embeddings = [item.embedding for item in response.data]
        
        logger.info(f"Generated {len(embeddings)} embeddings in batch")
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings batch: {e}")
        raise
