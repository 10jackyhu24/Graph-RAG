from fastapi import APIRouter, UploadFile, File, Form
from app.services.pipeline_service import run_pipeline

router = APIRouter()

@router.post("/process")
async def process(
    file: UploadFile = File(...),
    mode: str = Form("document"),
):
    return await run_pipeline(mode, file)
