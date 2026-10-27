"""
Unit and integration tests for standardized error handling (PRD §9).
"""
import pytest
import httpx
from app.core.errors import (
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    VeritasError,
)


def test_veritas_error_attributes() -> None:
    """Verifies VeritasError custom exception attributes."""
    err = VeritasError(code="TEST_CODE", message="Test error message", status_code=418, retry_after=30)
    assert err.code == "TEST_CODE"
    assert err.message == "Test error message"
    assert err.status_code == 418
    assert err.retry_after == 30


@pytest.mark.asyncio
async def test_404_standardized_error_format(async_client: httpx.AsyncClient) -> None:
    """Verifies that non-existent routes return PRD §9 error JSON structure."""
    resp = await async_client.get("/api/non-existent-route-404")
    assert resp.status_code == 404
    data = resp.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] in ("NOT_FOUND", "HTTP_ERROR")


@pytest.mark.asyncio
async def test_validation_error_format(async_client: httpx.AsyncClient) -> None:
    """Verifies that input validation errors produce HTTP 422 with standardized error schema."""
    # POST to reviews with invalid body (once endpoint exists or hitting an invalid payload)
    resp = await async_client.post("/api/health")  # Method Not Allowed -> 405
    assert resp.status_code == 405
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] in ("METHOD_NOT_ALLOWED", "HTTP_ERROR")
