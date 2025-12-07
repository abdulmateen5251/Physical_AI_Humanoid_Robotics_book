"""Database connection and utilities for async Postgres."""

from typing import AsyncGenerator
import asyncpg
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Async Postgres database connection manager."""
    
    def __init__(self):
        """Initialize database manager."""
        self.pool: asyncpg.Pool = None
        
    async def connect(self) -> None:
        """Create database connection pool."""
        try:
            # Parse database URL to extract components
            # Format: postgresql+asyncpg://user:pass@host:port/dbname
            db_url = settings.database_url.replace("postgresql+asyncpg://", "")
            
            logger.info("Connecting to database...")
            self.pool = await asyncpg.create_pool(
                f"postgresql://{db_url}",
                min_size=2,
                max_size=10,
                command_timeout=60,
                timeout=30
            )
            logger.info("Database connection pool created")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def get_connection(self) -> asyncpg.Connection:
        """Get a connection from the pool."""
        if not self.pool:
            await self.connect()
        return await self.pool.acquire()
    
    async def release_connection(self, conn: asyncpg.Connection) -> None:
        """Release connection back to pool."""
        await self.pool.release(conn)


# Global database instance
database = Database()


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency for database connection.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: asyncpg.Connection = Depends(get_db)):
            result = await db.fetch("SELECT * FROM table")
    """
    conn = await database.get_connection()
    try:
        yield conn
    finally:
        await database.release_connection(conn)


async def init_db() -> None:
    """Initialize database connection on startup."""
    await database.connect()


async def close_db() -> None:
    """Close database connection on shutdown."""
    await database.disconnect()
