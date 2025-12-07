"""Acceptance tests for RAG accuracy on Module 1 questions."""

import pytest
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any

from app.services.rag_agent import rag_agent


# Load acceptance test questions
ACCEPTANCE_TESTS_FILE = Path(__file__).parent / "module-01.json"


def load_acceptance_tests() -> List[Dict[str, Any]]:
    """Load acceptance test questions from JSON file."""
    with open(ACCEPTANCE_TESTS_FILE, "r") as f:
        return json.load(f)


def calculate_topic_coverage(answer: str, expected_topics: List[str]) -> float:
    """Calculate what percentage of expected topics are covered in the answer.
    
    Args:
        answer: Generated answer text
        expected_topics: List of keywords/topics that should appear
        
    Returns:
        Coverage percentage (0.0 to 1.0)
    """
    answer_lower = answer.lower()
    covered_topics = sum(1 for topic in expected_topics if topic.lower() in answer_lower)
    return covered_topics / len(expected_topics) if expected_topics else 0.0


def is_answer_valid(answer: str, expected_topics: List[str], min_coverage: float = 0.5) -> bool:
    """Validate if answer meets acceptance criteria.
    
    An answer is valid if:
    1. It's not empty
    2. It's not an error message
    3. It covers at least min_coverage of expected topics
    
    Args:
        answer: Generated answer text
        expected_topics: List of expected topics
        min_coverage: Minimum topic coverage required (0.0 to 1.0)
        
    Returns:
        True if answer is valid
    """
    # Check for empty or error responses
    if not answer or len(answer.strip()) < 20:
        return False
    
    error_phrases = [
        "don't have enough information",
        "cannot answer",
        "no relevant information",
        "i don't know"
    ]
    
    if any(phrase in answer.lower() for phrase in error_phrases):
        return False
    
    # Check topic coverage
    coverage = calculate_topic_coverage(answer, expected_topics)
    return coverage >= min_coverage


@pytest.mark.asyncio
@pytest.mark.acceptance
async def test_module_01_rag_accuracy():
    """Test RAG accuracy on Module 1 acceptance questions.
    
    Acceptance Criteria:
    - Overall accuracy >= 90%
    - At least 50% topic coverage per answer
    - No error responses for valid questions
    """
    # Load test questions
    test_cases = load_acceptance_tests()
    
    if not test_cases:
        pytest.skip("No acceptance tests found in module-01.json")
    
    print(f"\n{'='*60}")
    print(f"Running {len(test_cases)} Module 1 Acceptance Tests")
    print(f"{'='*60}\n")
    
    results = []
    
    # Run each test case
    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        expected_topics = test_case["expected_topics"]
        difficulty = test_case.get("difficulty", "medium")
        
        print(f"Test {i}/{len(test_cases)}: {question[:60]}...")
        
        try:
            # Call RAG agent
            result = await rag_agent.answer_question(
                question=question,
                scope="fullbook",
                module_filter="module-01-ros2",
                top_k=10
            )
            
            answer = result["answer"]
            sources = result["sources"]
            score_avg = result["retrieval_score_avg"]
            
            # Validate answer
            is_valid = is_answer_valid(answer, expected_topics)
            coverage = calculate_topic_coverage(answer, expected_topics)
            
            results.append({
                "id": test_case["id"],
                "question": question,
                "answer": answer,
                "expected_topics": expected_topics,
                "topic_coverage": coverage,
                "retrieval_score": score_avg,
                "num_sources": len(sources),
                "is_valid": is_valid,
                "difficulty": difficulty
            })
            
            # Print result
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"  {status} | Coverage: {coverage:.1%} | Sources: {len(sources)} | Score: {score_avg:.3f}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            results.append({
                "id": test_case["id"],
                "question": question,
                "error": str(e),
                "is_valid": False,
                "difficulty": difficulty
            })
    
    # Calculate overall accuracy
    valid_count = sum(1 for r in results if r["is_valid"])
    accuracy = valid_count / len(results) if results else 0.0
    
    # Calculate average coverage
    avg_coverage = sum(r.get("topic_coverage", 0) for r in results) / len(results) if results else 0.0
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Acceptance Test Results Summary")
    print(f"{'='*60}")
    print(f"Total Questions:     {len(results)}")
    print(f"Valid Answers:       {valid_count}")
    print(f"Failed Answers:      {len(results) - valid_count}")
    print(f"Overall Accuracy:    {accuracy:.1%}")
    print(f"Avg Topic Coverage:  {avg_coverage:.1%}")
    print(f"{'='*60}\n")
    
    # Breakdown by difficulty
    difficulties = {}
    for result in results:
        diff = result["difficulty"]
        if diff not in difficulties:
            difficulties[diff] = {"total": 0, "valid": 0}
        difficulties[diff]["total"] += 1
        if result["is_valid"]:
            difficulties[diff]["valid"] += 1
    
    print("Accuracy by Difficulty:")
    for diff, stats in sorted(difficulties.items()):
        acc = stats["valid"] / stats["total"] if stats["total"] > 0 else 0.0
        print(f"  {diff.capitalize()}: {acc:.1%} ({stats['valid']}/{stats['total']})")
    
    print()
    
    # Save detailed results
    results_file = Path(__file__).parent / "module-01-results.json"
    with open(results_file, "w") as f:
        json.dump({
            "accuracy": accuracy,
            "avg_coverage": avg_coverage,
            "results": results
        }, f, indent=2)
    
    print(f"Detailed results saved to: {results_file}\n")
    
    # Assert acceptance criteria
    assert accuracy >= 0.90, f"RAG accuracy {accuracy:.1%} is below required 90%"
    assert avg_coverage >= 0.50, f"Average topic coverage {avg_coverage:.1%} is below required 50%"


@pytest.mark.asyncio
@pytest.mark.acceptance
async def test_retrieval_quality():
    """Test that retrieval returns relevant chunks for Module 1 questions."""
    from app.services.retrieval import retrieval_service
    
    test_cases = load_acceptance_tests()
    
    if not test_cases:
        pytest.skip("No acceptance tests found")
    
    print(f"\n{'='*60}")
    print(f"Testing Retrieval Quality")
    print(f"{'='*60}\n")
    
    retrieval_scores = []
    
    for test_case in test_cases[:5]:  # Test first 5 questions
        question = test_case["question"]
        
        # Retrieve chunks
        results = await retrieval_service.retrieve_chunks(
            question=question,
            top_k=5,
            module_filter="module-01-ros2"
        )
        
        if results:
            avg_score = sum(r.score for r in results) / len(results)
            retrieval_scores.append(avg_score)
            print(f"Q: {question[:50]}...")
            print(f"   Top-5 Avg Score: {avg_score:.3f}")
        else:
            print(f"Q: {question[:50]}...")
            print(f"   No results found!")
    
    if retrieval_scores:
        overall_avg = sum(retrieval_scores) / len(retrieval_scores)
        print(f"\nOverall Average Retrieval Score: {overall_avg:.3f}")
        print(f"{'='*60}\n")
        
        # Retrieval should have good relevance scores
        assert overall_avg >= 0.70, f"Retrieval score {overall_avg:.3f} is too low"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s", "-m", "acceptance"])
