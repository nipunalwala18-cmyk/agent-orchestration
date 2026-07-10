from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.conversation import ConversationRepository
from app.db.models import Conversation


class ConversationService:
    """Service layer coordinating business logic around Conversations."""

    def __init__(self, db: AsyncSession) -> None:
        self.conversation_repo = ConversationRepository(db)

    async def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Fetch a conversation by database identifier."""
        return await self.conversation_repo.get(conversation_id)

    async def list_conversations(
        self, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """Fetch a paginated list of conversations."""
        return await self.conversation_repo.get_all(skip, limit)

    async def create_conversation(self, conversation: Conversation) -> Conversation:
        """Create and store a new conversation database record."""
        return await self.conversation_repo.create(conversation)

    async def delete_conversation(self, conversation_id: int) -> bool:
        """Delete an existing conversation database record."""
        return await self.conversation_repo.delete(conversation_id)
