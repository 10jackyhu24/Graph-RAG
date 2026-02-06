from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.pipelines.context import PipelineContext
from app.pipelines.document_pipeline import DocumentPipeline
from app.pipelines.ingestion_pipeline import IngestionPipeline

router = APIRouter()


@router.post("/ingest")
async def ingest(
    file: UploadFile = File(None),
    text: str = Form(None),
    tenant_id: str = Form("default"),
    llm_provider: str = Form(None),
    llm_model: str = Form(None),
    source_type: str = Form(None),
    agent_id: str = Form(None),
):
    if file is None and not text:
        raise HTTPException(status_code=400, detail="file or text is required")
    ctx = PipelineContext(
        file=file,
        text=text,
        tenant_id=tenant_id,
        source_type=source_type,
        llm_provider=llm_provider,
        llm_model=llm_model,
        agent_id=agent_id,
    )
    pipeline = IngestionPipeline()
    result = await pipeline.run(ctx)

    return {
        "extraction": (
            result.extraction.model_dump(mode="json")
            if hasattr(result.extraction, "model_dump")
            else result.extraction
        ),
        "markdown": result.markdown,
        "source_type": result.source_type,
        "storage": result.storage_result,
    }


@router.post("/process")
async def process(
    file: UploadFile = File(None),
    text: str = Form(None),
    mode: str = Form("document"),
    tenant_id: str = Form("default"),
    llm_provider: str = Form(None),
    llm_model: str = Form(None),
    source_type: str = Form(None),
    agent_id: str = Form(None),
):
    ctx = None
    pipeline = None

    if mode == "document":
        ctx = PipelineContext(file=file)
        pipeline = DocumentPipeline()
    elif mode == "ingest":
        if file is None and not text:
            raise HTTPException(status_code=400, detail="file or text is required")
        ctx = PipelineContext(
            file=file,
            text=text,
            tenant_id=tenant_id,
            source_type=source_type,
            llm_provider=llm_provider,
            llm_model=llm_model,
            agent_id=agent_id,
        )
        pipeline = IngestionPipeline()
    else:
        return {"error": "Unsupported mode"}

    result = await pipeline.run(ctx)

    if mode == "ingest":
        return {
            "extraction": (
                result.extraction.model_dump(mode="json")
                if hasattr(result.extraction, "model_dump")
                else result.extraction
            ),
            "markdown": result.markdown,
            "source_type": result.source_type,
            "storage": result.storage_result,
        }

    return result.pdf_json
    # return StreamingResponse(
    #     io.BytesIO(result.pdf_bytes),
    #     media_type="application/pdf",
    #     headers={
    #         "Content-Disposition": "inline; filename=summary.pdf"
    #     }
    # )
