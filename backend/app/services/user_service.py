from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.user import UserRepository
from app.db.models import User


class UserService:
    """Service layer coordinating business logic around User operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: int) -> Optional[User]:
        """Fetch a user by database identifier."""
        return await self.user_repo.get(user_id)

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Fetch a paginated list of users."""
        return await self.user_repo.get_all(skip, limit)

    async def create_user(self, user: User) -> User:
        """Create and store a new user database record."""
        return await self.user_repo.create(user)

    async def delete_user(self, user_id: int) -> bool:
        """Delete an existing user database record."""
        return await self.user_repo.delete(user_id)
