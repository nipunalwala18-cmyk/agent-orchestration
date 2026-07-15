"""LangGraph workflow definition, independent of transport and API concerns."""

from langgraph.graph import END, StateGraph

from app.agents.planner import PlannerAgent
from app.memory.service import MemoryService
from app.tools.registry import ToolRegistry
from app.workflows.nodes import execute_tool, plan_request, update_memory
from app.workflows.state import OrchestrationState


def build_orchestration_graph(
    planner: PlannerAgent, tools: ToolRegistry, memory: MemoryService
):
    graph = StateGraph(OrchestrationState)

    async def planning_node(state: OrchestrationState):
        return await plan_request(state, planner)

    async def tool_node(state: OrchestrationState):
        return await execute_tool(state, tools)

    async def memory_node(state: OrchestrationState):
        return await update_memory(state, memory)

    graph.add_node("plan", planning_node)
    graph.add_node("tool", tool_node)
    graph.add_node("memory", memory_node)
    graph.set_entry_point("plan")
    graph.add_edge("plan", "tool")
    graph.add_edge("tool", "memory")
    graph.add_edge("memory", END)
    return graph.compile()
