from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.base import BaseRepository
from app.db.models import User


class UserRepository(BaseRepository[User]):
    """Repository handling database operations for the User model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)
