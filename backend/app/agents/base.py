from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """Abstract Base Class defining the operational blueprint for all orchestration agents."""

    def __init__(self, name: str, role: str) -> None:
        self.name = name
        self.role = role

    @abstractmethod
    async def run(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Run the main agent execution process."""
        pass

    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> bool:
        """Validate configuration settings and capability requirements."""
        pass

    @abstractmethod
    def handle_error(self, error: Exception) -> Any:
        """Standardized error recovery or fallback reporting routine."""
        pass

    @abstractmethod
    def report_status(self) -> Dict[str, Any]:
        """Retrieve telemetry, memory usage, and execution counts."""
        pass
