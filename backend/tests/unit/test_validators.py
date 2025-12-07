"""Unit tests for selection-mode validators."""

import pytest
from app.utils.validators import (
    validate_selection_answer,
    extract_facts,
    check_hallucination
)


def test_validate_selection_answer_valid():
    """Test validation with valid answer (all facts in selection)."""
    selected_text = """
    To create a publisher in rclpy, you use the create_publisher() method.
    The method takes three arguments: message type, topic name, and queue size.
    Example: self.publisher = self.create_publisher(String, 'topic', 10)
    """
    
    answer = """
    To create a publisher, use create_publisher() method.
    It takes message type, topic name, and queue size as arguments.
    """
    
    is_valid = validate_selection_answer(answer, selected_text)
    assert is_valid is True


def test_validate_selection_answer_invalid_hallucination():
    """Test validation with hallucinated facts."""
    selected_text = """
    ROS 2 uses DDS for communication. Publishers send messages to topics.
    """
    
    answer = """
    ROS 2 uses DDS for communication. Publishers send messages to topics.
    ROS 2 was released in 2015 and supports real-time systems.
    """
    # "released in 2015" is not in selected text
    
    is_valid = validate_selection_answer(answer, selected_text, threshold=0.8)
    assert is_valid is False


def test_validate_selection_answer_partial_match():
    """Test validation with partial word overlap."""
    selected_text = "A publisher node sends data to a topic."
    
    answer = "Publishers transmit information through topics."
    # Different wording but similar meaning
    
    # Should pass with lower threshold
    is_valid = validate_selection_answer(answer, selected_text, threshold=0.5)
    assert is_valid is True
    
    # Should fail with higher threshold
    is_valid = validate_selection_answer(answer, selected_text, threshold=0.9)
    assert is_valid is False


def test_extract_facts():
    """Test fact extraction from text."""
    text = """
    ROS 2 is a middleware framework. It supports multiple platforms.
    How does it work? Very short. This is another complete sentence.
    """
    
    facts = extract_facts(text)
    
    # Should extract statements, not questions or very short sentences
    assert len(facts) >= 2
    assert any("middleware" in f.lower() for f in facts)
    assert any("platforms" in f.lower() for f in facts)
    # Questions should be filtered out
    assert not any("?" in f for f in facts)


def test_check_hallucination_supported():
    """Test hallucination check with supported claim."""
    claim = "ROS 2 uses DDS for inter-process communication"
    sources = [
        "ROS 2 uses DDS middleware for inter-process communication.",
        "The publisher pattern is common in ROS 2."
    ]
    
    is_supported = check_hallucination(claim, sources, threshold=0.7)
    assert is_supported is True


def test_check_hallucination_not_supported():
    """Test hallucination check with unsupported claim."""
    claim = "ROS 2 was created by NASA in 2010"
    sources = [
        "ROS 2 uses DDS for communication.",
        "Publishers send messages to topics."
    ]
    
    is_supported = check_hallucination(claim, sources, threshold=0.7)
    assert is_supported is False


def test_validate_selection_answer_empty_answer():
    """Test validation with empty answer."""
    selected_text = "Some content here."
    answer = ""
    
    is_valid = validate_selection_answer(answer, selected_text)
    assert is_valid is True  # No claims to validate


def test_validate_selection_answer_short_claims():
    """Test that very short claims are skipped."""
    selected_text = "ROS 2 is good."
    answer = "Yes. No. Maybe. ROS 2 is good."
    
    # Very short claims should be skipped
    is_valid = validate_selection_answer(answer, selected_text)
    assert is_valid is True
