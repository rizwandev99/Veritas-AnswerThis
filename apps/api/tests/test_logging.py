"""
Unit tests for structured JSON logging and X-Request-ID propagation.
"""
import json
import logging
import pytest
import httpx
from app.core.logging import StructuredJSONFormatter, request_id_ctx


def test_structured_json_formatter() -> None:
    """Verifies that StructuredJSONFormatter formats records into valid JSON with expected keys."""
    formatter = StructuredJSONFormatter()
    token = request_id_ctx.set("test-request-id-123")
    try:
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Hello Veritas",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        data = json.loads(formatted)
        assert data["level"] == "INFO"
        assert data["message"] == "Hello Veritas"
        assert data["request_id"] == "test-request-id-123"
        assert "timestamp" in data
    finally:
        request_id_ctx.reset(token)


@pytest.mark.asyncio
async def test_request_id_header_propagation(async_client: httpx.AsyncClient, mock_db_manager: pytest.FixtureRequest) -> None:
    """Verifies X-Request-ID header is propagated or created by middleware."""
    # When client sends X-Request-ID
    custom_id = "req-client-xyz-789"
    resp = await async_client.get("/api/health", headers={"X-Request-ID": custom_id})
    assert resp.headers.get("X-Request-ID") == custom_id

    # When client doesn't send X-Request-ID
    resp2 = await async_client.get("/api/health")
    generated_id = resp2.headers.get("X-Request-ID")
    assert generated_id is not None
    assert len(generated_id) > 8
