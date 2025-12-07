"""Ingest documents to Qdrant vector database."""

import argparse
import asyncio
import os
import uuid
from pathlib import Path
from typing import List
from datetime import datetime
import logging

from app.models.document import DocumentChunk
from app.services.qdrant_client import qdrant_service
from app.utils.embeddings import generate_embeddings_batch
from app.utils.chunking import semantic_chunk_markdown, extract_keywords, classify_chunk_type
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ingest documents to Qdrant")
    parser.add_argument(
        "--docs",
        type=str,
        required=True,
        help="Path to docs directory"
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=settings.qdrant_collection,
        help="Qdrant collection name"
    )
    parser.add_argument(
        "--force-reindex",
        action="store_true",
        help="Force reindex (recreate collection)"
    )
    return parser.parse_args()


def extract_module_from_path(file_path: Path) -> str:
    """Extract module identifier from file path."""
    # Example: frontend/docs/module-01-ros2/chapter.md -> module-01-ros2
    parts = file_path.parts
    for part in parts:
        if part.startswith("module-"):
            return part
    return "unknown"


def extract_chapter_id(file_path: Path, docs_root: Path) -> str:
    """Extract chapter identifier from file path."""
    # Example: frontend/docs/module-01-ros2/02-nodes.md -> module-01-ros2/02-nodes
    relative_path = file_path.relative_to(docs_root)
    return str(relative_path.with_suffix("")).replace("\\", "/")


async def process_markdown_file(file_path: Path, docs_root: Path) -> List[DocumentChunk]:
    """Process a single markdown file into chunks."""
    logger.info(f"Processing file: {file_path}")
    
    # Read file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract metadata
    module = extract_module_from_path(file_path)
    chapter_id = extract_chapter_id(file_path, docs_root)
    
    # Chunk content
    raw_chunks = semantic_chunk_markdown(content, chapter_id, module)
    
    if not raw_chunks:
        logger.warning(f"No chunks generated for {file_path}")
        return []
    
    # Extract texts for batch embedding
    texts = [chunk["content"] for chunk in raw_chunks]
    
    # Generate embeddings in batch
    logger.info(f"Generating {len(texts)} embeddings...")
    embeddings = await generate_embeddings_batch(texts)
    
    # Create DocumentChunk objects
    chunks = []
    indexed_at = datetime.utcnow().isoformat() + "Z"
    
    for i, (raw_chunk, embedding) in enumerate(zip(raw_chunks, embeddings)):
        chunk = DocumentChunk(
            chunk_id=str(uuid.uuid4()),
            content=raw_chunk["content"],
            embedding=embedding,
            chapter_id=chapter_id,
            module=module,
            section=raw_chunk["section"],
            heading_path=raw_chunk["heading_path"],
            file_url=f"/docs/{chapter_id}",
            source_file=str(file_path),
            chunk_type=classify_chunk_type(raw_chunk["content"]),
            lang="en",
            keywords=extract_keywords(raw_chunk["content"]),
            indexed_at=indexed_at,
            chunk_index=i,
            total_chunks=len(raw_chunks)
        )
        chunks.append(chunk)
    
    logger.info(f"Created {len(chunks)} chunks from {file_path}")
    return chunks


async def ingest_documents(docs_path: str, collection_name: str, force_reindex: bool):
    """Ingest all markdown documents from directory."""
    docs_root = Path(docs_path)
    
    if not docs_root.exists():
        raise ValueError(f"Docs directory not found: {docs_path}")
    
    # Initialize collection
    logger.info(f"Initializing collection: {collection_name}")
    qdrant_service.collection_name = collection_name
    qdrant_service.init_collection(recreate=force_reindex)
    
    # Find all markdown files
    md_files = list(docs_root.rglob("*.md"))
    logger.info(f"Found {len(md_files)} markdown files")
    
    # Process files
    all_chunks = []
    for md_file in md_files:
        try:
            chunks = await process_markdown_file(md_file, docs_root)
            all_chunks.extend(chunks)
        except Exception as e:
            logger.error(f"Failed to process {md_file}: {e}")
            continue
    
    # Upsert to Qdrant in batches
    batch_size = 100
    logger.info(f"Upserting {len(all_chunks)} chunks in batches of {batch_size}")
    
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        qdrant_service.upsert_chunks(batch)
        logger.info(f"Upserted batch {i // batch_size + 1}/{(len(all_chunks) + batch_size - 1) // batch_size}")
    
    # Print summary
    logger.info("=" * 60)
    logger.info(f"Ingestion complete!")
    logger.info(f"Total chunks indexed: {len(all_chunks)}")
    logger.info(f"Collection: {collection_name}")
    logger.info("=" * 60)
    
    # Get collection info
    try:
        info = qdrant_service.get_collection_info()
        logger.info(f"Collection info: {info}")
    except Exception as e:
        logger.warning(f"Failed to get collection info: {e}")


async def main():
    """Main entry point."""
    args = parse_args()
    
    await ingest_documents(
        docs_path=args.docs,
        collection_name=args.collection,
        force_reindex=args.force_reindex
    )


if __name__ == "__main__":
    asyncio.run(main())
