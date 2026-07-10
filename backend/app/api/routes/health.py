import logging
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.db.session import get_db
from app.utils.redis import RedisClient
from app.api.dependencies import get_redis_client
from app.schemas.responses import APIResponse

logger = logging.getLogger("platform.health")
router = APIRouter()


@router.get("/health", response_model=APIResponse[dict[str, str]])
async def health_check(
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis_client),
) -> APIResponse[dict[str, str]]:
    """Verify database and Redis connectivity, returning structured system status."""
    db_status = "disconnected"
    redis_status = "disconnected"

    # Verify PostgreSQL connectivity
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")

    # Verify Redis connectivity
    try:
        if await redis.ping():
            redis_status = "connected"
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")

    is_healthy = db_status == "connected" and redis_status == "connected"
    api_status = "healthy" if is_healthy else "unhealthy"

    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return APIResponse(
        success=is_healthy,
        message="System status diagnostic results.",
        data={"database": db_status, "redis": redis_status, "api": api_status},
    )
