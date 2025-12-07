"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.document import DocumentChunk, QdrantSearchResult


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_chunks():
    """Sample document chunks."""
    chunk = DocumentChunk(
        chunk_id="chunk-001",
        content="ROS 2 is a middleware for robotics.",
        chapter_id="module-01-ros2",
        section="Introduction",
        heading_path=["Introduction", "What is ROS 2"],
        file_url="/docs/module-01-ros2/intro",
        keywords=["ros2", "middleware"],
        chunk_type="text",
        embedding=[0.1] * 1536,
        lang="en"
    )
    return [QdrantSearchResult(chunk=chunk, score=0.92)]


def test_retrieve_endpoint_success(client, sample_chunks):
    """Test successful retrieve endpoint call."""
    with patch('app.services.retrieval.retrieval_service.retrieve_chunks', new=AsyncMock(return_value=sample_chunks)):
        response = client.post(
            "/api/retrieve",
            json={
                "question": "What is ROS 2?",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["chunks"]) == 1
        assert data["chunks"][0]["chunk_id"] == "chunk-001"
        assert data["chunks"][0]["score"] == 0.92


def test_retrieve_endpoint_with_filters(client, sample_chunks):
    """Test retrieve endpoint with filters."""
    with patch('app.services.retrieval.retrieval_service.retrieve_chunks', new=AsyncMock(return_value=sample_chunks)):
        response = client.post(
            "/api/retrieve",
            json={
                "question": "What is ROS 2?",
                "top_k": 5,
                "module_filter": "module-01-ros2",
                "lang": "en"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["total"] == 1


def test_retrieve_endpoint_validation_error(client):
    """Test retrieve endpoint with invalid input."""
    response = client.post(
        "/api/retrieve",
        json={
            "question": "",  # Empty question
            "top_k": 10
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_answer_endpoint_fullbook_mode(client):
    """Test answer endpoint in fullbook mode."""
    mock_result = {
        "answer": "ROS 2 is a middleware framework.",
        "sources": [
            {
                "chapter_id": "module-01-ros2",
                "section": "Introduction",
                "file_url": "/docs/module-01-ros2",
                "heading_path": ["Introduction"],
                "score": 0.92
            }
        ],
        "chunk_ids": ["chunk-001"],
        "retrieval_score_avg": 0.92,
        "response_time_ms": 500,
        "scope": "fullbook"
    }
    
    with patch('app.services.rag_agent.rag_agent.answer_question', new=AsyncMock(return_value=mock_result)):
        response = client.post(
            "/api/answer",
            json={
                "question": "What is ROS 2?",
                "scope": "fullbook",
                "top_k": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "ROS 2 is a middleware framework."
        assert data["scope"] == "fullbook"
        assert len(data["sources"]) == 1
        assert data["response_time_ms"] == 500


def test_answer_endpoint_selection_mode(client):
    """Test answer endpoint in selection mode."""
    mock_result = {
        "answer": "This text describes ROS 2.",
        "sources": [],
        "chunk_ids": [],
        "retrieval_score_avg": 1.0,
        "response_time_ms": 300,
        "scope": "selected_text"
    }
    
    with patch('app.services.rag_agent.rag_agent.answer_question', new=AsyncMock(return_value=mock_result)):
        response = client.post(
            "/api/answer",
            json={
                "question": "What is this about?",
                "scope": "selected_text",
                "selected_text": "ROS 2 is a middleware for robotics."
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["scope"] == "selected_text"
        assert len(data["sources"]) == 0


def test_answer_endpoint_missing_selected_text(client):
    """Test answer endpoint with missing selected_text in selection mode."""
    response = client.post(
        "/api/answer",
        json={
            "question": "What is this?",
            "scope": "selected_text"
            # Missing selected_text
        }
    )
    
    assert response.status_code == 400
    assert "selected_text required" in response.json()["detail"]


def test_feedback_endpoint_success(client):
    """Test successful feedback submission."""
    mock_db = AsyncMock()
    mock_db.pool.fetchval.return_value = 123  # Feedback ID
    
    with patch('app.api.feedback.get_db', return_value=mock_db):
        response = client.post(
            "/api/feedback",
            json={
                "question": "What is ROS 2?",
                "answer": "ROS 2 is a middleware.",
                "rating": 5,
                "chunk_ids": ["chunk-001"],
                "scope": "fullbook"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["feedback_id"] == 123


def test_feedback_endpoint_validation_error(client):
    """Test feedback endpoint with invalid rating."""
    response = client.post(
        "/api/feedback",
        json={
            "question": "What is ROS 2?",
            "answer": "ROS 2 is a middleware.",
            "rating": 6,  # Invalid: must be 1-5
            "scope": "fullbook"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_feedback_stats_endpoint(client):
    """Test feedback statistics endpoint."""
    mock_db = AsyncMock()
    mock_db.pool.fetchrow.return_value = {
        "total_feedback": 100,
        "avg_rating": 4.5,
        "positive_count": 80,
        "negative_count": 10,
        "unique_sessions": 50
    }
    
    with patch('app.api.feedback.get_db', return_value=mock_db):
        response = client.get("/api/feedback/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_feedback"] == 100
        assert data["avg_rating"] == 4.5
        assert data["positive_count"] == 80


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
