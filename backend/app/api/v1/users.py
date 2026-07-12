from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.auth import UserOut
from app.schemas.responses import APIResponse
from app.services.user import UserService
from app.utils.decorators import require_permission

router = APIRouter()


@router.get("/", response_model=APIResponse[List[UserOut]])
@require_permission("users:read")
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> APIResponse[List[UserOut]]:
    """List all registered platform users. Requires 'users:read' permission."""
    user_service = UserService(db)
    users = await user_service.list_users(skip=skip, limit=limit)
    data = [UserOut.model_validate(u) for u in users]
    return APIResponse(
        success=True,
        message="User list retrieved successfully.",
        data=data,
    )
