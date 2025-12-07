"""Unit tests for RAG agent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.rag_agent import rag_agent, RAGAgent
from app.models.document import DocumentChunk, QdrantSearchResult


@pytest.fixture
def sample_search_results():
    """Sample search results."""
    chunk = DocumentChunk(
        chunk_id="chunk-001",
        content="ROS 2 is a middleware for robotics.",
        chapter_id="module-01-ros2",
        section="Introduction",
        heading_path=["Introduction"],
        file_url="/docs/module-01-ros2",
        keywords=["ros2"],
        chunk_type="text",
        embedding=[0.1] * 1536,
        lang="en"
    )
    return [QdrantSearchResult(chunk=chunk, score=0.92)]


@pytest.mark.asyncio
async def test_answer_question_fullbook_mode(sample_search_results):
    """Test answering question in fullbook mode."""
    with patch.object(rag_agent.retrieval, 'retrieve_chunks', new=AsyncMock(return_value=sample_search_results)):
        with patch.object(rag_agent.retrieval, 'format_context_for_llm', return_value="ROS 2 is a middleware for robotics."):
            with patch.object(rag_agent.llm, 'generate_answer', new=AsyncMock(return_value="ROS 2 is a middleware framework.")):
                with patch.object(rag_agent.llm, 'validate_answer_quality', new=AsyncMock(return_value={"is_valid": True})):
                    result = await rag_agent.answer_question(
                        question="What is ROS 2?",
                        scope="fullbook",
                        top_k=10
                    )
                    
                    assert result["answer"] == "ROS 2 is a middleware framework."
                    assert result["scope"] == "fullbook"
                    assert len(result["sources"]) == 1
                    assert len(result["chunk_ids"]) == 1
                    assert result["retrieval_score_avg"] == 0.92


@pytest.mark.asyncio
async def test_answer_question_selection_mode():
    """Test answering question in selection mode."""
    selected_text = "ROS 2 is a middleware for robotics."
    
    with patch.object(rag_agent.llm, 'generate_answer', new=AsyncMock(return_value="This text describes ROS 2 as a middleware.")):
        result = await rag_agent.answer_question(
            question="What does this say?",
            scope="selected_text",
            selected_text=selected_text
        )
        
        assert result["answer"] == "This text describes ROS 2 as a middleware."
        assert result["scope"] == "selected_text"
        assert len(result["sources"]) == 0  # No sources in selection mode
        assert result["retrieval_score_avg"] == 1.0


@pytest.mark.asyncio
async def test_answer_question_no_results():
    """Test answering when no chunks are found."""
    with patch.object(rag_agent.retrieval, 'retrieve_chunks', new=AsyncMock(return_value=[])):
        result = await rag_agent.answer_question(
            question="What is quantum computing?",
            scope="fullbook"
        )
        
        assert "don't have enough information" in result["answer"]
        assert len(result["sources"]) == 0
        assert result["retrieval_score_avg"] == 0.0


@pytest.mark.asyncio
async def test_answer_question_with_module_filter(sample_search_results):
    """Test answering with module filter."""
    with patch.object(rag_agent.retrieval, 'retrieve_chunks', new=AsyncMock(return_value=sample_search_results)) as mock_retrieve:
        with patch.object(rag_agent.retrieval, 'format_context_for_llm', return_value="ROS 2 is a middleware."):
            with patch.object(rag_agent.llm, 'generate_answer', new=AsyncMock(return_value="ROS 2 answer")):
                with patch.object(rag_agent.llm, 'validate_answer_quality', new=AsyncMock(return_value={"is_valid": True})):
                    result = await rag_agent.answer_question(
                        question="What is ROS 2?",
                        scope="fullbook",
                        module_filter="module-01-ros2",
                        top_k=5
                    )
                    
                    # Verify retrieve was called with correct filter
                    mock_retrieve.assert_called_once()
                    call_kwargs = mock_retrieve.call_args[1]
                    assert call_kwargs['module_filter'] == "module-01-ros2"
                    assert call_kwargs['top_k'] == 5


@pytest.mark.asyncio
async def test_answer_question_missing_selected_text():
    """Test that selection mode requires selected_text."""
    with pytest.raises(ValueError, match="selected_text required"):
        await rag_agent.answer_question(
            question="What is this?",
            scope="selected_text",
            selected_text=None
        )


@pytest.mark.asyncio
async def test_answer_question_response_time_tracking(sample_search_results):
    """Test that response time is tracked."""
    with patch.object(rag_agent.retrieval, 'retrieve_chunks', new=AsyncMock(return_value=sample_search_results)):
        with patch.object(rag_agent.retrieval, 'format_context_for_llm', return_value="context"):
            with patch.object(rag_agent.llm, 'generate_answer', new=AsyncMock(return_value="answer")):
                with patch.object(rag_agent.llm, 'validate_answer_quality', new=AsyncMock(return_value={"is_valid": True})):
                    result = await rag_agent.answer_question(
                        question="What is ROS 2?",
                        scope="fullbook"
                    )
                    
                    assert "response_time_ms" in result
                    assert result["response_time_ms"] > 0
                    assert isinstance(result["response_time_ms"], int)
