import logging
import uuid
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.utils.redis import RedisClient, redis_client

logger = logging.getLogger("platform.dependencies")
security = HTTPBearer(auto_error=False)


async def get_redis_client() -> RedisClient:
    """Dependency provider that returns the global RedisClient wrapper."""
    return redis_client


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency to extract JWT from Authorization header and resolve User."""
    if not credentials:
        raise AppException("Missing authentication credentials.", status_code=401)

    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise AppException("Invalid token type.", status_code=401)

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AppException("Invalid token payload.", status_code=401)

        user_id = uuid.UUID(user_id_str)
        user_repo = UserRepository(db)
        user = await user_repo.get(user_id)

        if not user:
            raise AppException("User not found.", status_code=401)
        if not user.is_active:
            raise AppException("User account is disabled.", status_code=403)

        # Store user in request state for downstream middlewares or decorators
        request.state.user = user
        return user

    except jwt.ExpiredSignatureError:
        raise AppException("Access token has expired.", status_code=401)
    except (jwt.PyJWTError, ValueError):
        raise AppException("Invalid authentication token.", status_code=401)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify that the current user is active."""
    if not current_user.is_active:
        raise AppException("User is inactive.", status_code=403)
    return current_user


class PermissionChecker:
    """FastAPI dependency wrapper checking user permissions (RBAC)."""

    def __init__(self, required_permission: str) -> None:
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm.name)

        if self.required_permission not in user_permissions:
            logger.warning(
                f"User {current_user.email} denied access to permission: {self.required_permission}"
            )
            raise AppException("Permission denied.", status_code=403)

        return current_user
