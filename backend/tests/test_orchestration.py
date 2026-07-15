import pytest

from app.agents.planner import PlannerAgent
from app.agents.registry import AgentRegistry
from app.memory.inmemory import InMemoryStore
from app.memory.service import MemoryService
from app.tools.dummy import DummyTool
from app.tools.email import EmailTool
from app.tools.rag import RAGTool
from app.tools.registry import ToolRegistry
from app.tools.sql import SQLTool
from app.tools.web_search import WebSearchTool
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


@pytest.mark.parametrize(
    ("user_input", "expected_tool"),
    [
        ("Search the web for orchestration patterns", "web_search"),
        ("Query the database with SQL", "sql"),
        ("Send an email to the customer", "email"),
        ("Search our knowledge base documentation", "rag"),
    ],
)
async def test_planner_selects_registered_tool_by_intent(
    user_input: str, expected_tool: str
) -> None:
    tools = ToolRegistry()
    for tool in (DummyTool(), WebSearchTool(), SQLTool(), EmailTool(), RAGTool()):
        tools.register(tool)

    plan = await PlannerAgent(tools).run(user_input)

    assert plan.steps[0].tool_name == expected_tool
    assert plan.steps[0].arguments == {"input_text": user_input}


async def test_registry_enforces_tool_permissions() -> None:
    tools = ToolRegistry()
    tools.register(WebSearchTool())

    with pytest.raises(PermissionError, match="chat:write"):
        await tools.execute("web_search", granted_permissions=set(), input_text="test")


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
    assert await store.get_workflow_state("conversation-1") == {
        "last_tool": "dummy",
        "last_response": "Dummy Tool processed: validate workflow",
    }


async def test_follow_up_resolves_previous_result() -> None:
    store = InMemoryStore()
    tools = ToolRegistry()
    tools.register(DummyTool())
    tools.register(EmailTool())
    engine = WorkflowEngine(PlannerAgent(tools), tools, MemoryService(store))

    await engine.execute("Generate sales report", conversation_id="conversation-2")
    state = await engine.execute("Email it", conversation_id="conversation-2")

    assert state["plan"].steps[0].tool_name == "email"
    assert "Dummy Tool processed: Generate sales report" in state["response"]


async def test_workflow_streams_lifecycle_events() -> None:
    tools = ToolRegistry()
    tools.register(DummyTool())
    engine = WorkflowEngine(PlannerAgent(), tools, MemoryService(InMemoryStore()))

    events = [event async for event in engine.stream("stream this")]

    assert [event.message for event in events] == [
        "Planning request...",
        "Loaded conversation memory...",
        "Planner selected Dummy Tool...",
        "Executing Dummy Tool...",
        "Updating Memory...",
        "Workflow Complete...",
    ]
