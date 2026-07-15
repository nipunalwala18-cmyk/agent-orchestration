"""Execution facade over the reusable LangGraph workflow."""

from dataclasses import dataclass
from typing import AsyncIterator, Dict, Optional
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
        "plan": "Planner selected Dummy Tool...",
        "tool": "Executing Dummy Tool...",
        "memory": "Updating Memory...",
    }

    def __init__(self, planner: PlannerAgent, tools: ToolRegistry, memory: MemoryService) -> None:
        self._graph = build_orchestration_graph(planner, tools, memory)

    @staticmethod
    def _initial_state(request: str, conversation_id: Optional[str]) -> OrchestrationState:
        return {"request": request, "conversation_id": conversation_id or str(uuid4())}

    async def execute(self, request: str, conversation_id: Optional[str] = None) -> OrchestrationState:
        return await self._graph.ainvoke(self._initial_state(request, conversation_id))

    async def stream(
        self, request: str, conversation_id: Optional[str] = None
    ) -> AsyncIterator[WorkflowEvent]:
        yield WorkflowEvent("status", "Planning request...")
        async for update in self._graph.astream(
            self._initial_state(request, conversation_id), stream_mode="updates"
        ):
            for node_name, state_update in update.items():
                data: Optional[Dict[str, str]] = None
                if node_name == "plan":
                    plan = state_update["plan"]
                    data = {"tool_name": plan.steps[0].tool_name}
                elif node_name == "tool":
                    data = {"response": state_update["response"]}
                yield WorkflowEvent("status", self._EVENTS[node_name], data)
        yield WorkflowEvent("complete", "Workflow Complete...")
