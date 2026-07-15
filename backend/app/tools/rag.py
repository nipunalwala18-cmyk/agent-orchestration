"""RAG tool contract placeholder for a future retrieval adapter."""

from typing import Any, Dict, FrozenSet

from app.tools.base import BaseTool


class RAGTool(BaseTool):
    """Provides deterministic retrieval acknowledgement without a vector database."""

    async def execute(self, **kwargs: Any) -> Dict[str, str]:
        query = kwargs["input_text"].strip()
        return {"output": f"RAG Tool queued retrieval request: {query}"}

    def validate(self, **kwargs: Any) -> bool:
        return isinstance(kwargs.get("input_text"), str) and bool(kwargs["input_text"].strip())

    def permissions(self) -> FrozenSet[str]:
        return frozenset({"chat:write"})

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "rag",
            "description": "Retrieves grounded context through a future knowledge adapter.",
            "args_schema": {"input_text": "string"},
        }
