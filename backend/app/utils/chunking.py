"""Markdown chunking utilities for semantic document splitting."""

from typing import List, Dict, Tuple
import re
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 characters)."""
    return len(text) // 4


def semantic_chunk_markdown(
    content: str,
    chapter_id: str,
    module: str,
    min_tokens: int = None,
    max_tokens: int = None
) -> List[Dict]:
    """Chunk markdown content semantically at heading boundaries.
    
    Args:
        content: Markdown content to chunk
        chapter_id: Chapter identifier
        module: Module identifier
        min_tokens: Minimum chunk size (default: from settings)
        max_tokens: Maximum chunk size (default: from settings)
        
    Returns:
        List of chunk dictionaries with content and metadata
    """
    if min_tokens is None:
        min_tokens = settings.chunk_size_min
    if max_tokens is None:
        max_tokens = settings.chunk_size_max
    
    chunks = []
    
    # Split by headings (H2 and H3)
    # Pattern matches: ## Heading or ### Heading
    heading_pattern = r'^(#{2,3})\s+(.+)$'
    
    lines = content.split('\n')
    current_chunk = []
    current_heading = None
    current_level = 1
    heading_stack = []
    
    for line in lines:
        heading_match = re.match(heading_pattern, line)
        
        if heading_match:
            # Save previous chunk if it exists and meets size requirements
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                token_count = estimate_tokens(chunk_text)
                
                if token_count >= min_tokens:
                    chunks.append({
                        'content': chunk_text,
                        'section': current_heading or 'Introduction',
                        'heading_path': ' > '.join(heading_stack) if heading_stack else module,
                        'token_count': token_count
                    })
                elif chunks:
                    # Merge with previous chunk if too small
                    chunks[-1]['content'] += '\n\n' + chunk_text
                    chunks[-1]['token_count'] = estimate_tokens(chunks[-1]['content'])
            
            # Start new chunk
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            
            # Update heading stack
            if level == 2:
                heading_stack = [heading]
            elif level == 3:
                if len(heading_stack) == 0:
                    heading_stack = [heading]
                else:
                    heading_stack = heading_stack[:1] + [heading]
            
            current_heading = heading
            current_level = level
            current_chunk = [line]
        else:
            current_chunk.append(line)
        
        # Check if chunk exceeds max size
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            token_count = estimate_tokens(chunk_text)
            
            if token_count > max_tokens:
                # Split at paragraph boundary
                paragraphs = chunk_text.split('\n\n')
                if len(paragraphs) > 1:
                    # Save first part
                    split_point = len(paragraphs) // 2
                    first_part = '\n\n'.join(paragraphs[:split_point])
                    second_part = '\n\n'.join(paragraphs[split_point:])
                    
                    chunks.append({
                        'content': first_part,
                        'section': current_heading or 'Introduction',
                        'heading_path': ' > '.join(heading_stack) if heading_stack else module,
                        'token_count': estimate_tokens(first_part)
                    })
                    
                    current_chunk = [second_part]
    
    # Save final chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        token_count = estimate_tokens(chunk_text)
        
        if token_count >= min_tokens:
            chunks.append({
                'content': chunk_text,
                'section': current_heading or 'Introduction',
                'heading_path': ' > '.join(heading_stack) if heading_stack else module,
                'token_count': token_count
            })
        elif chunks:
            chunks[-1]['content'] += '\n\n' + chunk_text
            chunks[-1]['token_count'] = estimate_tokens(chunks[-1]['content'])
    
    logger.info(f"Chunked document into {len(chunks)} chunks (chapter: {chapter_id})")
    
    return chunks


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple frequency-based approach).
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords
    """
    # Remove common words (simplified stopwords)
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
        'these', 'those', 'it', 'its', 'you', 'your', 'we', 'our', 'they'
    }
    
    # Extract words (alphanumeric only)
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Filter stopwords and count frequency
    word_freq = {}
    for word in words:
        if word not in stopwords:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:max_keywords]]
    
    return keywords


def classify_chunk_type(content: str) -> str:
    """Classify chunk as content, code, or exercise.
    
    Args:
        content: Chunk content
        
    Returns:
        Chunk type: "content", "code", or "exercise"
    """
    # Check for code blocks
    if '```' in content or '    ' in content:
        return 'code'
    
    # Check for exercise keywords
    exercise_keywords = ['exercise', 'lab', 'assignment', 'quiz', 'question', 'task']
    content_lower = content.lower()
    
    for keyword in exercise_keywords:
        if keyword in content_lower:
            return 'exercise'
    
    return 'content'
