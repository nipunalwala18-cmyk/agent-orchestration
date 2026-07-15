"""Email tool contract placeholder for a future provider adapter."""

from typing import Any, Dict, FrozenSet

from app.tools.base import BaseTool


class EmailTool(BaseTool):
    """Produces a deterministic dispatch acknowledgement without sending email."""

    async def execute(self, **kwargs: Any) -> Dict[str, str]:
        message = kwargs["input_text"].strip()
        return {"output": f"Email Tool queued message request: {message}"}

    def validate(self, **kwargs: Any) -> bool:
        return isinstance(kwargs.get("input_text"), str) and bool(kwargs["input_text"].strip())

    def permissions(self) -> FrozenSet[str]:
        return frozenset({"chat:write"})

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "email",
            "description": "Sends email through a future provider adapter.",
            "args_schema": {"input_text": "string"},
        }
