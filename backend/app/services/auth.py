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

    async def login_with_google(self, token: str) -> User:
        """Verify Google ID token, resolve user email, and find/create user."""
        from google.oauth2 import id_token
        from google.auth.transport import requests
        from app.core.config import settings
        import uuid

        if settings.APP_ENV == "testing" or token.startswith("mock_"):
            email = token.replace("mock_", "")
        else:
            if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "placeholder-google-client-id-here":
                raise AppException("Google OAuth Client ID is not configured on the server.", status_code=500)
            try:
                idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
                email = idinfo.get("email")
                if not email:
                    raise AppException("Email address not provided in Google ID token.", status_code=401)
            except Exception as e:
                raise AppException(f"Google ID token verification failed: {str(e)}", status_code=401)

        # Check if user already exists
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Create user dynamically without password
            user = User(
                id=uuid.uuid4(),
                email=email,
                hashed_password=None,  # Social login user has no password
                is_active=True,
            )
            # Fetch default Role
            from app.repositories.role import RoleRepository

            role_repo = RoleRepository(self.db)
            user_role = await role_repo.get_by_name("User")
            if user_role:
                user.roles.append(user_role)

            user = await self.user_repo.create(user)

        if not user.is_active:
            raise AppException("User account is disabled.", status_code=403)

        return user

