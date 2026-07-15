"""Purely focused async graph nodes."""

from typing import Any, Dict

from app.agents.planner import PlannerAgent
from app.memory.service import MemoryService
from app.tools.registry import ToolRegistry
from app.workflows.state import OrchestrationState


async def plan_request(state: OrchestrationState, planner: PlannerAgent) -> Dict[str, Any]:
    return {"plan": await planner.run(state["request"], {"history": state.get("history", [])})}


async def execute_tool(state: OrchestrationState, tools: ToolRegistry) -> Dict[str, Any]:
    plan = state["plan"]
    step = plan.steps[0]
    result = await tools.execute(step.tool_name, input_text=step.input_text)
    return {"tool_result": result, "response": str(result["output"])}


async def update_memory(state: OrchestrationState, memory: MemoryService) -> Dict[str, Any]:
    await memory.record_exchange(state["conversation_id"], state["request"], state["response"])
    return {}
