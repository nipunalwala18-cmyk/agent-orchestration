"""Redis short-term memory adapter for conversation and workflow state."""

import json
from datetime import datetime
from typing import Any, Dict, List

from app.memory.base import MemoryMessage, MemoryStore
from app.utils.redis import RedisClient


class RedisMemoryStore(MemoryStore):
    """Stores bounded conversation data in Redis using JSON list/hash values."""

    def __init__(self, client: RedisClient, ttl_seconds: int = 86_400) -> None:
        self._client = client
        self._ttl_seconds = ttl_seconds

    async def _redis(self):
        if self._client.client is None:
            await self._client.connect()
        if self._client.client is None:
            raise RuntimeError("Redis memory client is not connected.")
        return self._client.client

    @staticmethod
    def _messages_key(conversation_id: str) -> str:
        return f"memory:conversation:{conversation_id}:messages"

    @staticmethod
    def _state_key(conversation_id: str) -> str:
        return f"memory:conversation:{conversation_id}:workflow"

    async def get_history(self, conversation_id: str) -> List[MemoryMessage]:
        redis = await self._redis()
        raw_messages = await redis.lrange(self._messages_key(conversation_id), 0, -1)
        return [self._decode_message(value) for value in raw_messages]

    async def append(self, conversation_id: str, message: MemoryMessage) -> None:
        redis = await self._redis()
        key = self._messages_key(conversation_id)
        await redis.rpush(key, json.dumps(self._encode_message(message)))
        await redis.expire(key, self._ttl_seconds)

    async def get_workflow_state(self, conversation_id: str) -> Dict[str, Any]:
        redis = await self._redis()
        value = await redis.get(self._state_key(conversation_id))
        return json.loads(value) if value else {}

    async def save_workflow_state(
        self, conversation_id: str, state: Dict[str, Any]
    ) -> None:
        redis = await self._redis()
        await redis.setex(
            self._state_key(conversation_id), self._ttl_seconds, json.dumps(state, default=str)
        )

    @staticmethod
    def _encode_message(message: MemoryMessage) -> Dict[str, str]:
        return {
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        }

    @staticmethod
    def _decode_message(value: str) -> MemoryMessage:
        payload = json.loads(value)
        return MemoryMessage(
            role=payload["role"],
            content=payload["content"],
            created_at=datetime.fromisoformat(payload["created_at"]),
        )
