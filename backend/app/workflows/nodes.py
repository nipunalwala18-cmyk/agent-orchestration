"""Purely focused async graph nodes."""

from typing import Any, Dict

from app.agents.planner import PlannerAgent
from app.memory.service import MemoryService
from app.tools.registry import ToolRegistry
from app.workflows.state import OrchestrationState


async def load_memory(state: OrchestrationState, memory: MemoryService) -> Dict[str, Any]:
    return {
        "history": await memory.history(state["conversation_id"]),
        "workflow_state": await memory.workflow_state(state["conversation_id"]),
    }


async def plan_request(state: OrchestrationState, planner: PlannerAgent) -> Dict[str, Any]:
    return {"plan": await planner.run(state["request"], {"history": state.get("history", [])})}


async def execute_tool(state: OrchestrationState, tools: ToolRegistry) -> Dict[str, Any]:
    plan = state["plan"]
    step = plan.steps[0]
    result = await tools.execute(
        step.tool_name,
        granted_permissions=state.get("permissions"),
        **step.arguments,
    )
    return {
        "tool_result": {**result, "tool_name": step.tool_name},
        "response": str(result["output"]),
    }


async def update_memory(state: OrchestrationState, memory: MemoryService) -> Dict[str, Any]:
    await memory.record_exchange(state["conversation_id"], state["request"], state["response"])
    await memory.save_workflow_state(
        state["conversation_id"],
        {
            "last_tool": state["plan"].steps[0].tool_name,
            "last_response": state["response"],
        },
    )
    return {}
