from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.base import BaseRepository
from app.db.models import Conversation


class ConversationRepository(BaseRepository[Conversation]):
    """Repository handling database operations for the Conversation model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Conversation, db)
