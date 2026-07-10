from fastapi import APIRouter

router = APIRouter()


@router.get("/info")
async def get_info() -> dict[str, str]:
    """Retrieve basic information about the v1 API.

    Placeholder for future v1 routes.
    """
    return {
        "version": "v1",
        "description": "AI Orchestration Platform API Version 1",
    }
