"""A deterministic tool for validating orchestration end to end."""

from typing import Any, Dict

from app.tools.base import BaseTool


class DummyTool(BaseTool):
    """Echoes supplied text without relying on external systems."""

    async def execute(self, **kwargs: Any) -> Dict[str, str]:
        input_text = str(kwargs["input_text"]).strip()
        return {"output": f"Dummy Tool processed: {input_text}"}

    def validate(self, **kwargs: Any) -> bool:
        return isinstance(kwargs.get("input_text"), str) and bool(kwargs["input_text"].strip())

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "dummy",
            "description": "Echoes user input for orchestration validation.",
            "args_schema": {"input_text": "string"},
        }
