"""Unit tests for retrieval service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.retrieval import retrieval_service, RetrievalService
from app.models.document import DocumentChunk, QdrantSearchResult


@pytest.fixture
def sample_search_results():
    """Sample search results."""
    chunk1 = DocumentChunk(
        chunk_id="chunk-001",
        content="ROS 2 is a middleware for robotics.",
        chapter_id="module-01-ros2",
        section="Introduction to ROS 2",
        heading_path=["Introduction", "What is ROS 2"],
        file_url="/docs/module-01-ros2/intro",
        keywords=["ros2", "middleware", "robotics"],
        chunk_type="text",
        embedding=[0.1] * 1536,
        lang="en"
    )
    
    chunk2 = DocumentChunk(
        chunk_id="chunk-002",
        content="ROS 2 uses DDS for communication.",
        chapter_id="module-01-ros2",
        section="Architecture",
        heading_path=["Architecture", "DDS Layer"],
        file_url="/docs/module-01-ros2/architecture",
        keywords=["ros2", "dds", "communication"],
        chunk_type="text",
        embedding=[0.2] * 1536,
        lang="en"
    )
    
    return [
        QdrantSearchResult(chunk=chunk1, score=0.92),
        QdrantSearchResult(chunk=chunk2, score=0.85)
    ]


@pytest.mark.asyncio
async def test_retrieve_chunks_success(sample_search_results):
    """Test successful chunk retrieval."""
    with patch('app.services.retrieval.generate_embedding', new=AsyncMock(return_value=[0.5] * 1536)):
        with patch.object(retrieval_service.qdrant, 'search', return_value=sample_search_results):
            results = await retrieval_service.retrieve_chunks(
                question="What is ROS 2?",
                top_k=10
            )
            
            assert len(results) == 2
            assert results[0].chunk.chunk_id == "chunk-001"
            assert results[0].score == 0.92


@pytest.mark.asyncio
async def test_retrieve_chunks_with_filters(sample_search_results):
    """Test chunk retrieval with module filter."""
    with patch('app.services.retrieval.generate_embedding', new=AsyncMock(return_value=[0.5] * 1536)):
        with patch.object(retrieval_service.qdrant, 'search', return_value=sample_search_results) as mock_search:
            results = await retrieval_service.retrieve_chunks(
                question="What is ROS 2?",
                top_k=5,
                module_filter="module-01-ros2",
                lang="en"
            )
            
            # Verify search was called with correct filters
            mock_search.assert_called_once()
            call_kwargs = mock_search.call_args[1]
            assert call_kwargs['module_filter'] == "module-01-ros2"
            assert call_kwargs['lang_filter'] == "en"
            assert call_kwargs['top_k'] == 5


@pytest.mark.asyncio
async def test_retrieve_chunks_empty_results():
    """Test retrieval with no matching chunks."""
    with patch('app.services.retrieval.generate_embedding', new=AsyncMock(return_value=[0.5] * 1536)):
        with patch.object(retrieval_service.qdrant, 'search', return_value=[]):
            results = await retrieval_service.retrieve_chunks(
                question="What is quantum computing?"
            )
            
            assert len(results) == 0


def test_format_context_for_llm(sample_search_results):
    """Test context formatting for LLM."""
    context = retrieval_service.format_context_for_llm(sample_search_results)
    
    assert "Source 1" in context
    assert "Source 2" in context
    assert "ROS 2 is a middleware for robotics" in context
    assert "ROS 2 uses DDS for communication" in context
    assert "Score: 0.920" in context
    assert "module-01-ros2" in context


def test_format_context_length_limit(sample_search_results):
    """Test context length limiting."""
    # Set very small max length
    context = retrieval_service.format_context_for_llm(
        sample_search_results,
        max_context_length=100
    )
    
    # Should only include first chunk (or partial)
    assert len(context) <= 100


def test_get_source_citations(sample_search_results):
    """Test source citation extraction."""
    citations = retrieval_service.get_source_citations(sample_search_results)
    
    assert len(citations) == 2
    assert citations[0]["chapter_id"] == "module-01-ros2"
    assert citations[0]["section"] == "Introduction to ROS 2"
    assert citations[0]["score"] == 0.92
    assert citations[1]["score"] == 0.85
