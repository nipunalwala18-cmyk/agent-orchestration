"""Storage abstraction for orchestration conversation memory."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass(frozen=True)
class MemoryMessage:
    role: str
    content: str
    created_at: datetime


class MemoryStore(ABC):
    """Backend-neutral append-only conversation memory contract."""

    @abstractmethod
    async def get_history(self, conversation_id: str) -> List[MemoryMessage]:
        pass

    @abstractmethod
    async def append(self, conversation_id: str, message: MemoryMessage) -> None:
        pass

    @abstractmethod
    async def get_workflow_state(self, conversation_id: str) -> Dict[str, Any]:
        """Return persisted graph state for resuming a conversation."""
        pass

    @abstractmethod
    async def save_workflow_state(
        self, conversation_id: str, state: Dict[str, Any]
    ) -> None:
        """Persist graph state independently of conversation messages."""
        pass
