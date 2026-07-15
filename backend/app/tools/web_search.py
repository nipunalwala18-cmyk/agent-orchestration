"""Web-search tool contract placeholder for provider integration."""

from typing import Any, Dict, FrozenSet

from app.tools.base import BaseTool


class WebSearchTool(BaseTool):
    """Provides a deterministic result until a search provider is configured."""

    async def execute(self, **kwargs: Any) -> Dict[str, str]:
        query = kwargs["input_text"].strip()
        return {"output": f"Web Search queued for: {query}"}

    def validate(self, **kwargs: Any) -> bool:
        return isinstance(kwargs.get("input_text"), str) and bool(kwargs["input_text"].strip())

    def permissions(self) -> FrozenSet[str]:
        return frozenset({"chat:write"})

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "web_search",
            "description": "Searches public web sources for a user query.",
            "args_schema": {"input_text": "string"},
        }
