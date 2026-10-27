"""
Tests for CORS configuration and origin headers.
"""
import pytest
import httpx


@pytest.mark.asyncio
async def test_cors_preflight_allowed_origin(async_client: httpx.AsyncClient) -> None:
    """Verifies that CORS preflight from allowed origin returns appropriate headers."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Request-ID, Content-Type",
    }
    resp = await async_client.options("/api/health", headers=headers)
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


@pytest.mark.asyncio
async def test_cors_preflight_disallowed_origin(async_client: httpx.AsyncClient) -> None:
    """Verifies that unauthorized origins are not returned in access-control-allow-origin."""
    headers = {
        "Origin": "http://malicious-site.example.com",
        "Access-Control-Request-Method": "GET",
    }
    resp = await async_client.options("/api/health", headers=headers)
    assert resp.headers.get("access-control-allow-origin") != "http://malicious-site.example.com"
