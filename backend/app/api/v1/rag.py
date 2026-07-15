from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from typing import Optional

from app.api.dependencies import get_current_user
from app.schemas.responses import APIResponse
from app.services.rag_service import RAGService
from app.utils.decorators import require_permission

try:
    from fastapi import UploadFile as FastAPIUploadFile
except Exception:  # pragma: no cover - defensive fallback
    FastAPIUploadFile = UploadFile

router = APIRouter()
rag_service = RAGService()


@router.post("/upload", response_model=APIResponse[dict[str, object]])
@require_permission("chat:write")
async def upload_document(
    request: Request,
    file: FastAPIUploadFile = File(...),
    source_name: Optional[str] = Form(None),
    current_user=Depends(get_current_user),
) -> APIResponse[dict[str, object]]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file name is required")

    contents = await file.read()
    stored = rag_service.upload_document(contents, source_name or file.filename)
    return APIResponse(
        success=True,
        message="Document uploaded successfully.",
        data=stored,
    )


@router.post("/query", response_model=APIResponse[dict[str, object]])
@require_permission("chat:write")
async def query_documents(
    request: Request,
    question: Annotated[str, Form(...)],
    top_k: Annotated[int, Form()] = 3,
    current_user=Depends(get_current_user),
) -> APIResponse[dict[str, object]]:
    result = await rag_service.query(question, top_k=top_k)
    return APIResponse(
        success=True,
        message="RAG answer generated.",
        data=result,
    )
