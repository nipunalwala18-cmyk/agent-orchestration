"""Application service that shields workflows from memory storage details."""

from datetime import datetime, timezone
from typing import List

from app.memory.base import MemoryMessage, MemoryStore


class MemoryService:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    async def history(self, conversation_id: str) -> List[MemoryMessage]:
        return await self._store.get_history(conversation_id)

    async def record_exchange(
        self, conversation_id: str, user_input: str, assistant_output: str
    ) -> None:
        now = datetime.now(timezone.utc)
        await self._store.append(conversation_id, MemoryMessage("user", user_input, now))
        await self._store.append(
            conversation_id, MemoryMessage("assistant", assistant_output, now)
        )
