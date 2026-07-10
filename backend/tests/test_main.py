from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

# Mark all test functions in this module as async
pytestmark = pytest.mark.asyncio


async def test_read_root(client: AsyncClient) -> None:
    """Test that GET / returns the correct status and metadata wrapped in APIResponse."""
    response = await client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"] == {
        "status": "ok",
        "service": "AI Orchestration Platform",
    }


async def test_health_check_healthy(client: AsyncClient) -> None:
    """Test that GET /health returns 200 and healthy status wrapped in APIResponse."""
    response = await client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"] == {
        "database": "connected",
        "redis": "connected",
        "api": "healthy",
    }


async def test_health_check_db_failure(client: AsyncClient, mock_db: AsyncMock) -> None:
    """Test that GET /health returns 503 when the database check fails."""
    mock_db.execute.side_effect = Exception("DB Connection lost")

    response = await client.get("/health")
    assert response.status_code == 503
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["data"] == {
        "database": "disconnected",
        "redis": "connected",
        "api": "unhealthy",
    }


async def test_health_check_redis_failure(
    client: AsyncClient, mock_redis: AsyncMock
) -> None:
    """Test that GET /health returns 503 when the Redis check fails."""
    mock_redis.ping.return_value = False

    response = await client.get("/health")
    assert response.status_code == 503
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["data"] == {
        "database": "connected",
        "redis": "disconnected",
        "api": "unhealthy",
    }
