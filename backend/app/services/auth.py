from datetime import datetime, timezone
from typing import Dict
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.utils.redis import redis_client


class AuthService:
    """Service layer coordinating business logic around User Authentication & JWT Sessioning."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate a user using credentials."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AppException("Invalid email or password.", status_code=401)
        if not user.is_active:
            raise AppException("User account is disabled.", status_code=403)
        if not verify_password(password, user.hashed_password):
            raise AppException("Invalid email or password.", status_code=401)
        return user

    async def create_tokens(self, user: User) -> Dict[str, str]:
        """Generate Access and Refresh tokens for authenticated user session."""
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Validate refresh token and issue a new access token."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AppException("Invalid token type.", status_code=401)

            user_id = payload.get("sub")
            if not user_id:
                raise AppException("Invalid token payload.", status_code=401)

            # Check blacklist in Redis
            redis = redis_client.client
            if redis:
                is_blacklisted = await redis.get(f"blacklist:{refresh_token}")
                if is_blacklisted:
                    raise AppException("Token has been revoked.", status_code=401)

            user = await self.user_repo.get(user_id)
            if not user or not user.is_active:
                raise AppException("User not found or disabled.", status_code=401)

            # Issue new access token
            new_access_token = create_access_token(subject=user.id)
            return {
                "access_token": new_access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        except jwt.ExpiredSignatureError:
            raise AppException("Refresh token has expired.", status_code=401)
        except jwt.PyJWTError:
            raise AppException("Invalid refresh token.", status_code=401)

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token by blacklisting it in Redis."""
        try:
            payload = decode_token(refresh_token)
            exp = payload.get("exp")
            if exp:
                now = datetime.now(timezone.utc).timestamp()
                ttl = int(exp - now)
                if ttl > 0:
                    redis = redis_client.client
                    if redis:
                        await redis.setex(f"blacklist:{refresh_token}", ttl, "revoked")
        except jwt.PyJWTError:
            # Token is already invalid, no need to blacklist
            pass
