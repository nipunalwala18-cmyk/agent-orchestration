"""Long-term memory port for PostgreSQL-backed repositories.

The application deliberately keeps storage schema decisions outside orchestration.
Deployments provide a repository implementing this small protocol (for example a
SQLAlchemy repository backed by a memory table and user-preferences table).
"""

from typing import Any, Dict, List, Protocol

from app.memory.base import MemoryMessage, MemoryStore


class PostgresMemoryRepository(Protocol):
    async def load_messages(self, conversation_id: str) -> List[MemoryMessage]: ...

    async def save_message(self, conversation_id: str, message: MemoryMessage) -> None: ...

    async def load_state(self, conversation_id: str) -> Dict[str, Any]: ...

    async def save_state(self, conversation_id: str, state: Dict[str, Any]) -> None: ...


class PostgresMemoryStore(MemoryStore):
    """Adapter that delegates durable memory to an injected PostgreSQL repository."""

    def __init__(self, repository: PostgresMemoryRepository) -> None:
        self._repository = repository

    async def get_history(self, conversation_id: str) -> List[MemoryMessage]:
        return await self._repository.load_messages(conversation_id)

    async def append(self, conversation_id: str, message: MemoryMessage) -> None:
        await self._repository.save_message(conversation_id, message)

    async def get_workflow_state(self, conversation_id: str) -> Dict[str, Any]:
        return await self._repository.load_state(conversation_id)

    async def save_workflow_state(
        self, conversation_id: str, state: Dict[str, Any]
    ) -> None:
        await self._repository.save_state(conversation_id, state)
