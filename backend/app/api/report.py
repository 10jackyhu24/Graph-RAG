from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import StreamingResponse
import io

from app.services.report_service import build_pdf_report, generate_note

router = APIRouter()


class ReportRequest(BaseModel):
    payload: dict
    language: str = "zh"
    llm_provider: str | None = None
    llm_model: str | None = None


@router.post("/report/pdf")
def report_pdf(req: ReportRequest):
    pdf_bytes = build_pdf_report(req.payload, req.language)
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")


@router.post("/report/note")
async def report_note(req: ReportRequest):
    note = await generate_note(req.payload, req.language, req.llm_provider, req.llm_model)
    return {"note": note}
