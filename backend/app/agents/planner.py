"""Deterministic planning agent used by the orchestration foundation."""

from dataclasses import asdict, dataclass
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.agents.base import BaseAgent

if TYPE_CHECKING:
    from app.tools.registry import ToolRegistry


@dataclass(frozen=True)
class PlanStep:
    """One executable step in an agent plan."""

    tool_name: str
    input_text: str
    purpose: str
    arguments: Dict[str, Any]


@dataclass(frozen=True)
class ExecutionPlan:
    """A provider-neutral plan that can grow to contain multiple tool steps."""

    summary: str
    steps: List[PlanStep]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PlannerAgent(BaseAgent):
    """Creates executable plans without coupling workflows to an LLM provider.

    Selects an available tool by intent and exposes a provider-neutral plan.
    """

    _INTENT_TO_TOOL = (
        (("email", "send mail", "send an email"), "email"),
        (("sql", "select ", "database", "query the db"), "sql"),
        (("rag", "knowledge base", "documentation", "document"), "rag"),
        (("web", "search", "news", "internet", "latest"), "web_search"),
    )

    def __init__(
        self, tool_registry: Optional["ToolRegistry"] = None, default_tool_name: str = "dummy"
    ) -> None:
        super().__init__(name="planner", role="workflow planner")
        self._tool_registry = tool_registry
        self.default_tool_name = default_tool_name
        self._execution_count = 0

    async def run(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        if not input_text or not input_text.strip():
            raise ValueError("A non-empty request is required to create a plan.")
        self._execution_count += 1
        contextual_input = self._resolve_references(input_text, context or {})
        tool_name = self._select_tool(contextual_input)
        return ExecutionPlan(
            summary=f"Execute the {tool_name} tool for the user request.",
            steps=[
                PlanStep(
                    tool_name=tool_name,
                    input_text=contextual_input,
                    purpose=f"Handle request using the selected {tool_name} capability.",
                    arguments={"input_text": contextual_input},
                )
            ],
        )

    @staticmethod
    def _resolve_references(input_text: str, context: Dict[str, Any]) -> str:
        """Resolve simple conversational references from the latest assistant turn."""
        history = context.get("history", [])
        previous_output = next(
            (message.content for message in reversed(history) if message.role == "assistant"),
            None,
        )
        if not previous_output:
            return input_text.strip()
        if re.search(r"\b(it|that|this)\b", input_text, flags=re.IGNORECASE):
            return f"{input_text.strip()} (referencing previous result: {previous_output})"
        return input_text.strip()

    def _select_tool(self, input_text: str) -> str:
        normalized = input_text.casefold()
        for phrases, tool_name in self._INTENT_TO_TOOL:
            if any(phrase in normalized for phrase in phrases) and self._is_available(tool_name):
                return tool_name
        if self._is_available(self.default_tool_name):
            return self.default_tool_name
        raise ValueError("No registered tool is available for this request.")

    def _is_available(self, tool_name: str) -> bool:
        return self._tool_registry is None or self._tool_registry.has(tool_name)

    def validate(self, config: Dict[str, Any]) -> bool:
        return bool(config.get("default_tool_name", self.default_tool_name))

    def handle_error(self, error: Exception) -> Dict[str, str]:
        return {"agent": self.name, "error": str(error)}

    def report_status(self) -> Dict[str, Any]:
        return {"name": self.name, "executions": self._execution_count}
