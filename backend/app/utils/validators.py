"""Validators for selection-mode fact checking."""

from typing import List
import re
import logging

logger = logging.getLogger(__name__)


def validate_selection_answer(answer: str, selected_text: str, threshold: float = 0.8) -> bool:
    """Validate that answer contains only facts from selected text.
    
    This is a critical function for US2 (selection mode) to ensure 100% fact verification.
    
    Args:
        answer: Generated answer text
        selected_text: User-selected text (ground truth)
        threshold: Similarity threshold (0-1)
        
    Returns:
        True if answer is valid (all facts in selection), False otherwise
    """
    try:
        # Extract claims from answer (sentences ending with . ! ?)
        answer_sentences = re.split(r'[.!?]+', answer)
        answer_claims = [s.strip() for s in answer_sentences if s.strip()]
        
        # Normalize texts for comparison
        selected_normalized = selected_text.lower().strip()
        
        # Check each claim
        invalid_claims = []
        
        for claim in answer_claims:
            claim_normalized = claim.lower().strip()
            
            # Skip very short claims (< 10 chars)
            if len(claim_normalized) < 10:
                continue
            
            # Check if claim appears in selected text (substring match)
            if claim_normalized in selected_normalized:
                continue
            
            # Check for semantic similarity (word overlap)
            claim_words = set(re.findall(r'\b\w+\b', claim_normalized))
            selected_words = set(re.findall(r'\b\w+\b', selected_normalized))
            
            # Calculate word overlap ratio
            overlap = len(claim_words & selected_words)
            similarity = overlap / len(claim_words) if claim_words else 0
            
            if similarity < threshold:
                invalid_claims.append(claim)
                logger.warning(f"Invalid claim detected (similarity: {similarity:.2f}): {claim}")
        
        # Validation passes if no invalid claims
        is_valid = len(invalid_claims) == 0
        
        if not is_valid:
            logger.error(f"Selection-mode validation failed: {len(invalid_claims)} invalid claims")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False


def extract_facts(text: str) -> List[str]:
    """Extract factual statements from text.
    
    Args:
        text: Input text
        
    Returns:
        List of factual statements (sentences)
    """
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    
    # Filter out very short sentences and questions
    facts = [
        s.strip() 
        for s in sentences 
        if s.strip() and len(s.strip()) > 15 and '?' not in s
    ]
    
    return facts


def check_hallucination(claim: str, source_texts: List[str], threshold: float = 0.7) -> bool:
    """Check if a claim is hallucinated (not supported by sources).
    
    Args:
        claim: Claim to verify
        source_texts: List of source documents
        threshold: Similarity threshold
        
    Returns:
        True if claim is supported by sources, False if hallucinated
    """
    claim_normalized = claim.lower().strip()
    
    for source in source_texts:
        source_normalized = source.lower().strip()
        
        # Substring match
        if claim_normalized in source_normalized:
            return True
        
        # Word overlap check
        claim_words = set(re.findall(r'\b\w+\b', claim_normalized))
        source_words = set(re.findall(r'\b\w+\b', source_normalized))
        
        overlap = len(claim_words & source_words)
        similarity = overlap / len(claim_words) if claim_words else 0
        
        if similarity >= threshold:
            return True
    
    return False
