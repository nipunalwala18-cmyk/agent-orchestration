"""Thread-safe in-memory implementation for Phase 2."""

import asyncio
from collections import defaultdict
from typing import DefaultDict, List

from app.memory.base import MemoryMessage, MemoryStore


class InMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._conversations: DefaultDict[str, List[MemoryMessage]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def get_history(self, conversation_id: str) -> List[MemoryMessage]:
        async with self._lock:
            return list(self._conversations[conversation_id])

    async def append(self, conversation_id: str, message: MemoryMessage) -> None:
        async with self._lock:
            self._conversations[conversation_id].append(message)
