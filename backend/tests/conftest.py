import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_redis_client
from app.db.session import get_db
from app.main import app


# Fixtures override dependencies


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db() -> AsyncMock:
    """Fixture to mock the asynchronous SQLAlchemy database session."""
    db_session = AsyncMock()
    db_session.execute = AsyncMock()
    return db_session


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Fixture to mock the asynchronous Redis client."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    return redis_mock


@pytest.fixture
async def client(
    mock_db: AsyncMock, mock_redis: AsyncMock
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture providing an async HTTP client for the FastAPI app, overriding DB and Redis clients."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis_client] = lambda: mock_redis

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
