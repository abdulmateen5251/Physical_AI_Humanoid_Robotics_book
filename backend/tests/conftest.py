"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
import asyncpg

from app.services.qdrant_client import QdrantService
from app.services.database import Database


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_qdrant() -> Mock:
    """Mock Qdrant service for testing."""
    mock = Mock(spec=QdrantService)
    mock.init_collection = Mock()
    mock.upsert_chunks = Mock()
    mock.search = Mock(return_value=[])
    mock.get_collection_info = Mock(return_value={
        "name": "test_collection",
        "vectors_count": 0,
        "points_count": 0,
        "status": "green"
    })
    return mock


@pytest.fixture
async def mock_postgres() -> AsyncGenerator[Mock, None]:
    """Mock Postgres connection for testing."""
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.execute = AsyncMock()
    
    yield mock_conn


@pytest.fixture
def mock_database() -> Mock:
    """Mock Database service for testing."""
    mock = Mock(spec=Database)
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    mock.get_connection = AsyncMock()
    mock.release_connection = AsyncMock()
    return mock


@pytest.fixture
def mock_openai_embedding():
    """Mock OpenAI embedding response."""
    from unittest.mock import patch
    
    with patch("openai.embeddings.create") as mock_create:
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_create.return_value = mock_response
        yield mock_create


@pytest.fixture
def sample_document_chunk():
    """Sample DocumentChunk for testing."""
    from app.models.document import DocumentChunk
    
    return DocumentChunk(
        chunk_id="test-chunk-001",
        content="Sample content about ROS 2 publishers",
        embedding=[0.1] * 1536,
        chapter_id="module-01-ros2/02-nodes",
        module="module-01-ros2",
        section="Publisher Pattern",
        heading_path="Module 1 > ROS 2 > Publisher Pattern",
        file_url="/docs/module-01-ros2/02-nodes",
        source_file="frontend/docs/module-01-ros2/02-nodes.md",
        chunk_type="content",
        lang="en",
        keywords=["publisher", "rclpy"],
        indexed_at="2025-12-06T10:00:00Z",
        chunk_index=0,
        total_chunks=3
    )


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# ROS 2 Nodes and Topics

## Introduction

ROS 2 is a middleware framework for robotics applications.

## Publisher Pattern

To create a publisher in rclpy:

```python
self.publisher = self.create_publisher(String, 'topic', 10)
```

### Publishing Messages

Call publish method to send messages:

```python
msg = String()
msg.data = 'Hello ROS 2'
self.publisher.publish(msg)
```
"""


# Test client fixture will be added when FastAPI routes are created
