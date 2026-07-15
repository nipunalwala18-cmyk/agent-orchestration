import pytest

from app.agents.planner import PlannerAgent
from app.agents.registry import AgentRegistry
from app.memory.inmemory import InMemoryStore
from app.memory.service import MemoryService
from app.tools.dummy import DummyTool
from app.tools.registry import ToolRegistry
from app.workflows.engine import WorkflowEngine

pytestmark = pytest.mark.asyncio


async def test_planner_creates_dummy_tool_plan() -> None:
    plan = await PlannerAgent().run("Summarize this request")

    assert plan.steps[0].tool_name == "dummy"
    assert plan.steps[0].input_text == "Summarize this request"


async def test_registries_resolve_registered_components() -> None:
    planner = PlannerAgent()
    agents = AgentRegistry()
    agents.register(planner)
    tools = ToolRegistry()
    tools.register(DummyTool())

    assert agents.get("planner") is planner
    assert await tools.execute("dummy", input_text="ping") == {
        "output": "Dummy Tool processed: ping"
    }


async def test_workflow_executes_and_records_memory() -> None:
    store = InMemoryStore()
    tools = ToolRegistry()
    tools.register(DummyTool())
    engine = WorkflowEngine(PlannerAgent(), tools, MemoryService(store))

    state = await engine.execute("validate workflow", conversation_id="conversation-1")

    assert state["response"] == "Dummy Tool processed: validate workflow"
    assert state["plan"].steps[0].tool_name == "dummy"
    history = await store.get_history("conversation-1")
    assert [(message.role, message.content) for message in history] == [
        ("user", "validate workflow"),
        ("assistant", "Dummy Tool processed: validate workflow"),
    ]


async def test_workflow_streams_lifecycle_events() -> None:
    tools = ToolRegistry()
    tools.register(DummyTool())
    engine = WorkflowEngine(PlannerAgent(), tools, MemoryService(InMemoryStore()))

    events = [event async for event in engine.stream("stream this")]

    assert [event.message for event in events] == [
        "Planning request...",
        "Planner selected Dummy Tool...",
        "Executing Dummy Tool...",
        "Updating Memory...",
        "Workflow Complete...",
    ]
