"""Tool discovery and common execution interface."""

from typing import Any, Dict, Iterable, Type, TypeVar

from app.tools.base import BaseTool

ToolType = TypeVar("ToolType", bound=BaseTool)


class ToolRegistry:
    """Registers tool instances using the name declared in their metadata."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: ToolType) -> ToolType:
        name = tool.metadata().get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("Tool metadata must include a non-empty name.")
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")
        self._tools[name] = tool
        return tool

    def register_class(self, tool_class: Type[ToolType]) -> Type[ToolType]:
        """Register a no-argument tool class, supporting declarative startup setup."""
        self.register(tool_class())
        return tool_class

    def get(self, name: str) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Tool '{name}' is not registered.") from exc

    async def execute(self, name: str, **kwargs: Any) -> Any:
        tool = self.get(name)
        if not tool.validate(**kwargs):
            raise ValueError(f"Invalid input for tool '{name}'.")
        return await tool.execute(**kwargs)

    def names(self) -> Iterable[str]:
        return tuple(self._tools)
