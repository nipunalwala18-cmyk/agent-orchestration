from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Abstract Base Class defining the standard interface for all agent tools."""

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool operation."""
        pass

    @abstractmethod
    def validate(self, **kwargs: Any) -> bool:
        """Validate input arguments before execution."""
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Retrieve tool metadata (name, description, args schema) for agent integration."""
        pass
