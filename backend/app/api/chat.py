from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from app.services.rag_service import stream_rag_answer

router = APIRouter()


class ChatRequest(BaseModel):
    tenant_id: str
    query: str
    language: str = "zh"
    llm_provider: str | None = None
    llm_model: str | None = None


@router.post("/chat")
async def chat(payload: ChatRequest):
    async def event_stream():
        async for chunk in stream_rag_answer(
            tenant_id=payload.tenant_id,
            question=payload.query,
            language=payload.language,
            provider=payload.llm_provider,
            model=payload.llm_model,
        ):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain")
