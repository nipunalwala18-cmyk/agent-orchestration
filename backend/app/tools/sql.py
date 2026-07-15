"""SQL tool contract placeholder; no database access is performed in Phase 3."""

from typing import Any, Dict, FrozenSet

from app.tools.base import BaseTool


class SQLTool(BaseTool):
    """Validates read-only query intent pending a dedicated data-source adapter."""

    async def execute(self, **kwargs: Any) -> Dict[str, str]:
        query = kwargs["input_text"].strip()
        return {"output": f"SQL Tool queued a read-only query request: {query}"}

    def validate(self, **kwargs: Any) -> bool:
        return isinstance(kwargs.get("input_text"), str) and bool(kwargs["input_text"].strip())

    def permissions(self) -> FrozenSet[str]:
        return frozenset({"chat:write"})

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "sql",
            "description": "Executes approved read-only SQL through a future data adapter.",
            "args_schema": {"input_text": "string"},
        }
