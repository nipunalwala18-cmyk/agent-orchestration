from app.utils.redis import RedisClient, redis_client


async def get_redis_client() -> RedisClient:
    """Dependency provider that returns the global RedisClient wrapper."""
    return redis_client
