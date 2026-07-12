from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
    GoogleLoginRequest,
)
from app.schemas.responses import APIResponse
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=APIResponse[UserOut],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in: UserRegister, db: AsyncSession = Depends(get_db)
) -> APIResponse[UserOut]:
    """Register a new user account."""
    user_service = UserService(db)
    user = await user_service.register_user(
        email=user_in.email, password=user_in.password
    )
    return APIResponse(
        success=True,
        message="User registered successfully.",
        data=UserOut.model_validate(user),
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    credentials: UserLogin, db: AsyncSession = Depends(get_db)
) -> APIResponse[TokenResponse]:
    """Log in an existing user and retrieve session tokens."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        email=credentials.email, password=credentials.password
    )
    tokens = await auth_service.create_tokens(user)
    return APIResponse(
        success=True,
        message="User logged in successfully.",
        data=TokenResponse(**tokens),
    )


@router.post("/logout", response_model=APIResponse[None])
async def logout(
    request_data: TokenRefreshRequest, db: AsyncSession = Depends(get_db)
) -> APIResponse[None]:
    """Log out a user by revoking their refresh token."""
    auth_service = AuthService(db)
    await auth_service.logout(request_data.refresh_token)
    return APIResponse(
        success=True,
        message="User logged out successfully.",
        data=None,
    )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh(
    request_data: TokenRefreshRequest, db: AsyncSession = Depends(get_db)
) -> APIResponse[TokenResponse]:
    """Refresh access token using a valid refresh token."""
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_token(request_data.refresh_token)
    return APIResponse(
        success=True,
        message="Token refreshed successfully.",
        data=TokenResponse(**tokens),
    )


@router.get("/me", response_model=APIResponse[UserOut])
async def get_me(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserOut]:
    """Retrieve details of the currently authenticated user."""
    return APIResponse(
        success=True,
        message="Current user profile retrieved successfully.",
        data=UserOut.model_validate(current_user),
    )


@router.post("/google", response_model=APIResponse[TokenResponse])
async def google_login(
    payload: GoogleLoginRequest, db: AsyncSession = Depends(get_db)
) -> APIResponse[TokenResponse]:
    """Verify Google token, resolve/create user, and retrieve JWT session tokens."""
    auth_service = AuthService(db)
    user = await auth_service.login_with_google(payload.id_token)
    tokens = await auth_service.create_tokens(user)
    return APIResponse(
        success=True,
        message="Google authentication successful.",
        data=TokenResponse(**tokens),
    )

