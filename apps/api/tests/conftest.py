"""
Pytest fixtures for Veritas API tests.
Provides isolated test settings, mock asyncpg connection pool, and httpx AsyncClient.
"""
import pytest
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock
import httpx
# Pre-import will fail in Red phase until app is implemented
from app.core.config import Settings
from app.db.session import DatabaseManager
from app.main import app


@pytest.fixture
def mock_db_manager(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Provides a mocked database manager for offline unit tests."""
    mock_mgr = MagicMock(spec=DatabaseManager)
    mock_mgr.check_health = AsyncMock(return_value={
        "connected": True,
        "latency_ms": 1.25,
        "pgvector": True,
        "pgvector_version": "0.7.0",
        "error": None,
    })
    from app.api import health
    monkeypatch.setattr(health, "db_manager", mock_mgr)
    return mock_mgr


@pytest.fixture
async def async_client() -> AsyncIterator[httpx.AsyncClient]:
    """Provides an httpx AsyncClient bound to the FastAPI ASGI application."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
