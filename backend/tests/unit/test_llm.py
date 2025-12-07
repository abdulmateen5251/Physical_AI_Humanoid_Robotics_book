"""Unit tests for LLM service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.llm import llm_service, LLMService
from app.utils.prompts import RAG_SYSTEM_PROMPT, SELECTION_MODE_PROMPT


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="ROS 2 is a middleware framework for robotics applications."))
    ]
    mock_response.usage = Mock(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150
    )
    return mock_response


@pytest.mark.asyncio
async def test_generate_answer_fullbook_mode(mock_openai_response):
    """Test answer generation in fullbook mode."""
    context = "ROS 2 is a middleware for robotics. It uses DDS for communication."
    
    with patch.object(llm_service.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
        answer = await llm_service.generate_answer(
            question="What is ROS 2?",
            context=context,
            scope="fullbook"
        )
        
        assert "ROS 2" in answer
        assert "middleware" in answer


@pytest.mark.asyncio
async def test_generate_answer_selection_mode(mock_openai_response):
    """Test answer generation in selection mode."""
    selected_text = "ROS 2 is a middleware for robotics."
    
    with patch.object(llm_service.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
        answer = await llm_service.generate_answer(
            question="What is this about?",
            context=selected_text,
            scope="selected_text",
            selected_text=selected_text
        )
        
        assert "middleware" in answer.lower()


@pytest.mark.asyncio
async def test_generate_answer_empty_context():
    """Test answer generation with empty context."""
    answer = await llm_service.generate_answer(
        question="What is ROS 2?",
        context="",
        scope="fullbook"
    )
    
    # Should return error message
    assert "don't have enough" in answer or "no relevant" in answer.lower()


@pytest.mark.asyncio
async def test_generate_answer_calls_openai_with_correct_params(mock_openai_response):
    """Test that OpenAI API is called with correct parameters."""
    context = "ROS 2 is a middleware for robotics."
    
    with patch.object(llm_service.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)) as mock_create:
        await llm_service.generate_answer(
            question="What is ROS 2?",
            context=context,
            scope="fullbook"
        )
        
        # Verify API call
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        
        assert call_kwargs['model'] == llm_service.model
        assert call_kwargs['temperature'] == 0.3
        assert call_kwargs['max_tokens'] == 1000
        assert len(call_kwargs['messages']) == 2


@pytest.mark.asyncio
async def test_validate_answer_quality_valid_answer():
    """Test answer quality validation for valid answer."""
    question = "What is ROS 2?"
    answer = "ROS 2 is a middleware framework for robotics that provides communication infrastructure."
    context = "ROS 2 is a middleware for robotics."
    
    metrics = await llm_service.validate_answer_quality(question, answer, context)
    
    assert metrics["has_content"] is True
    assert metrics["min_length"] is True
    assert metrics["not_error_message"] is True
    assert metrics["is_valid"] is True


@pytest.mark.asyncio
async def test_validate_answer_quality_short_answer():
    """Test answer quality validation for too short answer."""
    question = "What is ROS 2?"
    answer = "A middleware."
    context = "ROS 2 is a middleware for robotics."
    
    metrics = await llm_service.validate_answer_quality(question, answer, context)
    
    assert metrics["has_content"] is True
    assert metrics["min_length"] is False
    assert metrics["is_valid"] is False


@pytest.mark.asyncio
async def test_validate_answer_quality_error_message():
    """Test answer quality validation for error message."""
    question = "What is ROS 2?"
    answer = "I don't have enough information in the textbook to answer this question."
    context = ""
    
    metrics = await llm_service.validate_answer_quality(question, answer, context)
    
    assert metrics["not_error_message"] is False
    assert metrics["is_valid"] is False
