"""Integration tests for application health endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints(async_client: AsyncClient):
    """Verify both /health and /api/health return operational status."""
    for path in ["/health", "/api/health"]:
        response = await async_client.get(path)
        assert response.status_code == 200
        payload = response.json()
        assert "status" in payload
        assert payload["service"] == "Inferaxis Backend"
        assert payload["version"] == "0.1.0"
        assert "timestamp" in payload
        assert "database" in payload
