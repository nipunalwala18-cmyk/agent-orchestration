from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling database operations for the User model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a single user by email address, with roles eagerly loaded."""
        result = await self.db.execute(
            select(User)
            .filter(User.email == email)
            .options(selectinload(User.roles))
        )
        return result.scalars().first()
