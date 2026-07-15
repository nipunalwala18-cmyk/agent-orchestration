"""Execution facade over the reusable LangGraph workflow."""

from dataclasses import dataclass
from typing import AsyncIterator, Dict, FrozenSet, Optional
from uuid import uuid4

from app.agents.planner import PlannerAgent
from app.memory.service import MemoryService
from app.tools.registry import ToolRegistry
from app.workflows.graph import build_orchestration_graph
from app.workflows.state import OrchestrationState


@dataclass(frozen=True)
class WorkflowEvent:
    event: str
    message: str
    data: Optional[Dict[str, str]] = None


class WorkflowEngine:
    """Runs and streams the default graph while exposing no LangGraph internals."""

    _EVENTS = {
        "load_memory": "Loaded conversation memory...",
        "plan": "Planner selected tool...",
        "tool": "Executing selected tool...",
        "memory": "Updating Memory...",
    }

    def __init__(self, planner: PlannerAgent, tools: ToolRegistry, memory: MemoryService) -> None:
        self._graph = build_orchestration_graph(planner, tools, memory)

    @staticmethod
    def _initial_state(
        request: str, conversation_id: Optional[str], permissions: Optional[FrozenSet[str]]
    ) -> OrchestrationState:
        state: OrchestrationState = {
            "request": request,
            "conversation_id": conversation_id or str(uuid4()),
        }
        if permissions is not None:
            state["permissions"] = permissions
        return state

    async def execute(
        self,
        request: str,
        conversation_id: Optional[str] = None,
        permissions: Optional[FrozenSet[str]] = None,
    ) -> OrchestrationState:
        return await self._graph.ainvoke(
            self._initial_state(request, conversation_id, permissions)
        )

    async def stream(
        self,
        request: str,
        conversation_id: Optional[str] = None,
        permissions: Optional[FrozenSet[str]] = None,
    ) -> AsyncIterator[WorkflowEvent]:
        yield WorkflowEvent("status", "Planning request...")
        async for update in self._graph.astream(
            self._initial_state(request, conversation_id, permissions), stream_mode="updates"
        ):
            for node_name, state_update in update.items():
                data: Optional[Dict[str, str]] = None
                if node_name == "plan":
                    plan = state_update["plan"]
                    data = {"tool_name": plan.steps[0].tool_name}
                elif node_name == "tool":
                    data = {"response": state_update["response"]}
                message = self._EVENTS.get(node_name, f"Workflow node {node_name} completed...")
                if node_name == "plan":
                    tool_label = plan.steps[0].tool_name.replace("_", " ").title()
                    message = f"Planner selected {tool_label} Tool..."
                if node_name == "tool":
                    tool_label = (
                        state_update["tool_result"].get("tool_name", "selected")
                        .replace("_", " ")
                        .title()
                    )
                    message = f"Executing {tool_label} Tool..."
                if node_name == "load_memory":
                    message = "Loaded conversation memory..."
                yield WorkflowEvent("status", message, data)
        yield WorkflowEvent("complete", "Workflow Complete...")
