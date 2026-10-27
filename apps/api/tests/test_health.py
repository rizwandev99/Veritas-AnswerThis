"""
Tests for System Health Probe (GET /api/health) per PRD §9, §12 and PROJECT.md Contract 1.
"""
from unittest.mock import AsyncMock
import pytest
import httpx
from app.api import health


@pytest.mark.asyncio
async def test_F0_AC2_health_endpoint_healthy(
    async_client: httpx.AsyncClient,
    mock_db_manager: pytest.FixtureRequest,
) -> None:
    """AC: When database is connected and pgvector available, returns HTTP 200 with status=healthy."""
    resp = await async_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["vector_store"] == "pgvector"
    assert "uptime_seconds" in data
    assert "version" in data
    assert "dependencies" in data
    assert data["dependencies"]["database"]["status"] == "connected"
    assert data["dependencies"]["pgvector"]["status"] == "available"


@pytest.mark.asyncio
async def test_F0_AC2_health_endpoint_degraded(
    async_client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC: When database is connected but pgvector is unavailable, returns HTTP 200 with status=degraded."""
    mock_mgr = AsyncMock()
    mock_mgr.check_health = AsyncMock(return_value={
        "connected": True,
        "latency_ms": 2.1,
        "pgvector": False,
        "pgvector_version": None,
        "error": None,
    })
    monkeypatch.setattr(health, "db_manager", mock_mgr)

    resp = await async_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "degraded"
    assert data["database"] == "connected"
    assert data["dependencies"]["pgvector"]["status"] == "unavailable"


@pytest.mark.asyncio
async def test_F0_AC2_health_endpoint_unhealthy_503(
    async_client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC: When database connection fails, returns HTTP 503 with status=unhealthy."""
    mock_mgr = AsyncMock()
    mock_mgr.check_health = AsyncMock(return_value={
        "connected": False,
        "latency_ms": None,
        "pgvector": False,
        "pgvector_version": None,
        "error": "Connection to PostgreSQL timed out",
    })
    monkeypatch.setattr(health, "db_manager", mock_mgr)

    resp = await async_client.get("/api/health")
    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "unhealthy"
    assert data["database"] == "disconnected"
    assert data["dependencies"]["database"]["status"] == "disconnected"
    assert data["dependencies"]["database"]["error"] == "Connection to PostgreSQL timed out"
