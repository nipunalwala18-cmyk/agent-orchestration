import logging
from typing import Optional
from redis.asyncio import Redis, from_url
from app.core.config import settings

logger = logging.getLogger("platform.redis")


class RedisClient:
    """Wrapper class for managing an asynchronous Redis connection."""

    def __init__(self, url: str) -> None:
        self.url: str = url
        self.client: Optional[Redis] = None

    async def connect(self) -> None:
        """Establish asynchronous Redis connection."""
        if not self.client:
            self.client = from_url(self.url, decode_responses=True)
            logger.info("Redis client connected successfully.")

    async def disconnect(self) -> None:
        """Close Redis client connection."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Redis client disconnected successfully.")

    async def ping(self) -> bool:
        """Ping Redis server to verify connectivity.

        Returns:
            True if connection is active, False otherwise.
        """
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return False


# Global singleton instance of RedisClient
redis_client = RedisClient(settings.REDIS_URL)
