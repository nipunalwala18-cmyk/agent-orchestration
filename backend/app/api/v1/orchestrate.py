"""Authenticated API transport for the Phase 2 orchestration workflow."""

import json
from functools import lru_cache
from typing import AsyncIterator, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.planner import PlannerAgent
from app.api.dependencies import get_current_user
from app.memory.inmemory import InMemoryStore
from app.memory.service import MemoryService
from app.schemas.responses import APIResponse
from app.tools.dummy import DummyTool
from app.tools.registry import ToolRegistry
from app.utils.decorators import require_permission
from app.workflows.engine import WorkflowEngine

router = APIRouter()


class OrchestrationRequest(BaseModel):
    request: str = Field(min_length=1, max_length=10_000)
    conversation_id: Optional[str] = Field(default=None, max_length=255)


class OrchestrationResult(BaseModel):
    conversation_id: str
    response: str
    tool_name: str


@lru_cache(maxsize=1)
def get_workflow_engine() -> WorkflowEngine:
    tools = ToolRegistry()
    tools.register(DummyTool())
    return WorkflowEngine(PlannerAgent(), tools, MemoryService(InMemoryStore()))


async def sse_events(body: OrchestrationRequest) -> AsyncIterator[str]:
    async for item in get_workflow_engine().stream(body.request, body.conversation_id):
        payload = {"message": item.message, "data": item.data}
        yield f"event: {item.event}\ndata: {json.dumps(payload)}\n\n"


@router.post("", response_model=APIResponse[OrchestrationResult])
@require_permission("chat:write")
async def orchestrate(
    body: OrchestrationRequest,
    request: Request,
    current_user=Depends(get_current_user),
) -> APIResponse[OrchestrationResult]:
    state = await get_workflow_engine().execute(body.request, body.conversation_id)
    return APIResponse(
        success=True,
        message="Workflow completed.",
        data=OrchestrationResult(
            conversation_id=state["conversation_id"],
            response=state["response"],
            tool_name=state["plan"].steps[0].tool_name,
        ),
    )


@router.post("/stream")
@require_permission("chat:write")
async def orchestrate_stream(
    body: OrchestrationRequest,
    request: Request,
    current_user=Depends(get_current_user),
) -> StreamingResponse:
    return StreamingResponse(
        sse_events(body),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
