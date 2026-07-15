"""Typed state shared by all nodes in the orchestration graph."""

from typing import Any, Dict, List, Optional, TypedDict

from app.agents.planner import ExecutionPlan
from app.memory.base import MemoryMessage


class OrchestrationState(TypedDict, total=False):
    request: str
    conversation_id: str
    history: List[MemoryMessage]
    plan: ExecutionPlan
    tool_result: Dict[str, Any]
    response: str
    error: Optional[str]
