import asyncio
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_current_user
from app.utils.decorators import require_permission

router = APIRouter()


async def mock_stream_response(prompt: str):
    """Simulates a word-by-word streaming response."""
    response_text = (
        f"This is a placeholder response from the platform. "
        f"We successfully received your prompt: '{prompt}'. "
        f"Future phases will connect this directly to localized LLMs, Memory, "
        f"and tool orchestrations."
    )
    for word in response_text.split(" "):
        yield f"data: {word}\n\n"
        await asyncio.sleep(0.08)


@router.post("/stream")
@require_permission("chat:write")
async def stream_chat(
    request: Request,
    prompt: str,
    current_user=Depends(get_current_user),
) -> StreamingResponse:
    """Placeholder chat streaming endpoint using Server-Sent Events (SSE)."""
    return StreamingResponse(
        mock_stream_response(prompt), media_type="text/event-stream"
    )
