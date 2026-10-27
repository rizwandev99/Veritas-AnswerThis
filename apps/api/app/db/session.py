"""
PostgreSQL Database Connection Manager using asyncpg.
Provides connection pooling, health checks, and pgvector extension verification.
"""
import time
from typing import Any, Dict, Optional
import asyncpg
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or settings.DATABASE_URL
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """Initializes the asyncpg connection pool."""
        if self.pool is not None:
            return
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=settings.DB_POOL_TIMEOUT_SECONDS,
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.pool = None

    async def disconnect(self) -> None:
        """Closes the connection pool."""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed")

    async def check_health(self) -> Dict[str, Any]:
        """Performs ping and pgvector health verification."""
        if self.pool is None:
            try:
                # Attempt lazy reconnect
                await self.connect()
            except Exception as e:
                return {
                    "connected": False,
                    "latency_ms": None,
                    "pgvector": False,
                    "pgvector_version": None,
                    "error": str(e),
                }

        if self.pool is None:
            return {
                "connected": False,
                "latency_ms": None,
                "pgvector": False,
                "pgvector_version": None,
                "error": "Connection to PostgreSQL timed out",
            }

        start = time.perf_counter()
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                latency_ms = round((time.perf_counter() - start) * 1000, 2)

                # Check pgvector extension
                row = await conn.fetchrow(
                    "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
                )
                if row:
                    return {
                        "connected": True,
                        "latency_ms": latency_ms,
                        "pgvector": True,
                        "pgvector_version": row["extversion"],
                        "error": None,
                    }
                else:
                    return {
                        "connected": True,
                        "latency_ms": latency_ms,
                        "pgvector": False,
                        "pgvector_version": None,
                        "error": None,
                    }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "connected": False,
                "latency_ms": None,
                "pgvector": False,
                "pgvector_version": None,
                "error": str(e),
            }


db_manager = DatabaseManager()
