from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.core.security import get_password_hash
from app.core.exceptions import AppException


class UserService:
    """Service layer coordinating business logic around User operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user by database identifier."""
        return await self.user_repo.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email."""
        return await self.user_repo.get_by_email(email)

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Fetch a paginated list of users."""
        return await self.user_repo.get_all(skip, limit)

    async def register_user(self, email: str, password: str) -> User:
        """Register a new user, hash the password, and assign default 'User' role."""
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise AppException(
                "A user with this email address already exists.", status_code=400
            )

        hashed_password = get_password_hash(password)
        new_user = User(
            id=uuid.uuid4(), email=email, hashed_password=hashed_password, is_active=True
        )

        # Assign default 'User' role
        user_role = await self.role_repo.get_by_name("User")
        if user_role:
            new_user.roles.append(user_role)

        return await self.user_repo.create(new_user)

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete an existing user database record."""
        return await self.user_repo.delete(user_id)
