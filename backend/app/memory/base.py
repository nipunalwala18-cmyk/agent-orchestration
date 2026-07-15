"""Storage abstraction for orchestration conversation memory."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List


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
