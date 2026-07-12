from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository handling database operations for the Conversation model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Conversation, db)
