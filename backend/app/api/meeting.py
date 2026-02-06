from fastapi import APIRouter, Form, UploadFile, File, HTTPException

from app.pipelines.context import PipelineContext
from app.pipelines.ingestion_pipeline import IngestionPipeline
from app.services.asr_service import transcribe_audio
from app.utils.file_storage import save_upload_file

router = APIRouter()


@router.post("/meeting/ingest")
async def meeting_ingest(
    text: str = Form(...),
    tenant_id: str = Form("default"),
    llm_provider: str = Form(None),
    llm_model: str = Form(None),
    agent_id: str = Form(None),
    language: str = Form("zh"),
):
    ctx = PipelineContext(
        text=text,
        tenant_id=tenant_id,
        source_type="meeting",
        llm_provider=llm_provider,
        llm_model=llm_model,
        agent_id=agent_id,
    )
    pipeline = IngestionPipeline()
    result = await pipeline.run(ctx)

    return {
        "extraction": result.extraction if isinstance(result.extraction, dict) else result.extraction.model_dump(mode="json"),
        "source_type": result.source_type,
        "storage": result.storage_result,
    }


@router.post("/meeting/asr")
async def meeting_asr(
    file: UploadFile = File(...),
    tenant_id: str = Form("default"),
    llm_provider: str = Form(None),
    llm_model: str = Form(None),
    agent_id: str = Form(None),
    language: str = Form("zh"),
):
    if not file:
        raise HTTPException(status_code=400, detail="audio file required")
    file_path = await save_upload_file(file)
    text = transcribe_audio(file_path, language=language)
    ctx = PipelineContext(
        text=text,
        tenant_id=tenant_id,
        source_type="meeting",
        llm_provider=llm_provider,
        llm_model=llm_model,
        agent_id=agent_id,
    )
    pipeline = IngestionPipeline()
    result = await pipeline.run(ctx)
    return {
        "transcript": text,
        "extraction": result.extraction if isinstance(result.extraction, dict) else result.extraction.model_dump(mode="json"),
        "source_type": result.source_type,
        "storage": result.storage_result,
    }
