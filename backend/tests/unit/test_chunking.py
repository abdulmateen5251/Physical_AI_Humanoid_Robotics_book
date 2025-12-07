"""Unit tests for markdown chunking utilities."""

import pytest
from app.utils.chunking import (
    semantic_chunk_markdown,
    estimate_tokens,
    extract_keywords,
    classify_chunk_type
)


def test_estimate_tokens():
    """Test token estimation."""
    text = "This is a test" * 100  # ~1400 chars
    tokens = estimate_tokens(text)
    assert 300 < tokens < 400  # Rough estimate


def test_semantic_chunk_markdown(sample_markdown_content):
    """Test semantic chunking of markdown."""
    chunks = semantic_chunk_markdown(
        content=sample_markdown_content,
        chapter_id="module-01-ros2/02-nodes",
        module="module-01-ros2",
        min_tokens=50,
        max_tokens=500
    )
    
    assert len(chunks) > 0
    
    # Verify chunk structure
    for chunk in chunks:
        assert "content" in chunk
        assert "section" in chunk
        assert "heading_path" in chunk
        assert "token_count" in chunk
        
        # Check token limits
        assert 50 <= chunk["token_count"] <= 600  # Some tolerance


def test_semantic_chunk_markdown_headings(sample_markdown_content):
    """Test that chunks respect heading boundaries."""
    chunks = semantic_chunk_markdown(
        content=sample_markdown_content,
        chapter_id="test",
        module="test-module",
        min_tokens=10,
        max_tokens=800
    )
    
    # Should have chunks for different sections
    sections = [chunk["section"] for chunk in chunks]
    assert len(sections) > 0
    assert any("Publisher" in s for s in sections)


def test_extract_keywords():
    """Test keyword extraction."""
    text = """
    ROS 2 is a robotics middleware. Publishers send messages to topics.
    Subscribers receive messages from topics. The rclpy library provides
    Python bindings for ROS 2.
    """
    
    keywords = extract_keywords(text, max_keywords=5)
    
    assert len(keywords) <= 5
    assert "ros" in keywords or "robotics" in keywords
    # Stopwords should be filtered out
    assert "the" not in keywords
    assert "is" not in keywords


def test_classify_chunk_type_content():
    """Test chunk type classification for content."""
    content = "This is a description of ROS 2 concepts and patterns."
    chunk_type = classify_chunk_type(content)
    assert chunk_type == "content"


def test_classify_chunk_type_code():
    """Test chunk type classification for code."""
    content = """
    Here is some code:
    ```python
    def hello():
        print("Hello")
    ```
    """
    chunk_type = classify_chunk_type(content)
    assert chunk_type == "code"


def test_classify_chunk_type_exercise():
    """Test chunk type classification for exercises."""
    content = "Exercise 1: Create a publisher node in ROS 2."
    chunk_type = classify_chunk_type(content)
    assert chunk_type == "exercise"
