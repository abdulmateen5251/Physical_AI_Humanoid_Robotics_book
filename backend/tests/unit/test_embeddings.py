"""Unit tests for embedding generation."""

import pytest
from unittest.mock import Mock, patch
from app.utils.embeddings import generate_embedding, generate_embeddings_batch


@pytest.mark.asyncio
async def test_generate_embedding(mock_openai_embedding):
    """Test single embedding generation."""
    text = "This is a test sentence about ROS 2 publishers."
    
    embedding = await generate_embedding(text)
    
    assert embedding is not None
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)
    mock_openai_embedding.assert_called_once()


@pytest.mark.asyncio
async def test_generate_embedding_empty_text():
    """Test embedding generation with empty text."""
    with pytest.raises(ValueError, match="Empty text"):
        await generate_embedding("")


@pytest.mark.asyncio
async def test_generate_embeddings_batch(mock_openai_embedding):
    """Test batch embedding generation."""
    texts = [
        "First sentence about ROS 2",
        "Second sentence about publishers",
        "Third sentence about topics"
    ]
    
    # Mock batch response
    mock_response = Mock()
    mock_response.data = [
        Mock(embedding=[0.1] * 1536),
        Mock(embedding=[0.2] * 1536),
        Mock(embedding=[0.3] * 1536)
    ]
    mock_openai_embedding.return_value = mock_response
    
    embeddings = await generate_embeddings_batch(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)
    mock_openai_embedding.assert_called_once()


@pytest.mark.asyncio
async def test_generate_embeddings_batch_filters_empty():
    """Test batch generation filters empty texts."""
    texts = ["Valid text", "", "  ", "Another valid text"]
    
    with patch("openai.embeddings.create") as mock_create:
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 1536),
            Mock(embedding=[0.2] * 1536)
        ]
        mock_create.return_value = mock_response
        
        embeddings = await generate_embeddings_batch(texts)
        
        # Should only process 2 valid texts
        assert len(embeddings) == 2
        call_args = mock_create.call_args
        assert len(call_args.kwargs["input"]) == 2
