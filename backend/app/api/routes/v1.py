from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.chat import router as chat_router
from app.api.v1.orchestrate import router as orchestrate_router
from app.api.routes.health import router as health_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(orchestrate_router, prefix="/orchestrate", tags=["orchestration"])
router.include_router(health_router, tags=["health"])


@router.get("/info")
async def get_info() -> dict[str, str]:
    """Retrieve basic information about the v1 API."""
    return {
        "version": "v1",
        "description": "AI Orchestration Platform API Version 1",
    }
