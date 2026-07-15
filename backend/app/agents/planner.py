"""Deterministic planning agent used by the orchestration foundation."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from app.agents.base import BaseAgent


@dataclass(frozen=True)
class PlanStep:
    """One executable step in an agent plan."""

    tool_name: str
    input_text: str
    purpose: str


@dataclass(frozen=True)
class ExecutionPlan:
    """A provider-neutral plan that can grow to contain multiple tool steps."""

    summary: str
    steps: List[PlanStep]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PlannerAgent(BaseAgent):
    """Creates executable plans without coupling workflows to an LLM provider.

    This first implementation deliberately chooses ``dummy`` for every request.
    Replacing ``run`` with structured LLM planning will not change consumers.
    """

    def __init__(self, default_tool_name: str = "dummy") -> None:
        super().__init__(name="planner", role="workflow planner")
        self.default_tool_name = default_tool_name
        self._execution_count = 0

    async def run(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        if not input_text or not input_text.strip():
            raise ValueError("A non-empty request is required to create a plan.")
        self._execution_count += 1
        return ExecutionPlan(
            summary="Execute the deterministic dummy tool for the user request.",
            steps=[
                PlanStep(
                    tool_name=self.default_tool_name,
                    input_text=input_text.strip(),
                    purpose="Produce a deterministic response while validating orchestration.",
                )
            ],
        )

    def validate(self, config: Dict[str, Any]) -> bool:
        return bool(config.get("default_tool_name", self.default_tool_name))

    def handle_error(self, error: Exception) -> Dict[str, str]:
        return {"agent": self.name, "error": str(error)}

    def report_status(self) -> Dict[str, Any]:
        return {"name": self.name, "executions": self._execution_count}
