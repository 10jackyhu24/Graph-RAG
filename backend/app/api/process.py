from fastapi import APIRouter, UploadFile, File, Form
from app.pipelines.context import PipelineContext
from app.pipelines.document_pipeline import DocumentPipeline
from starlette.responses import StreamingResponse
import io

router = APIRouter()

@router.post("/process")
async def process(
    file: UploadFile = File(...),
    mode: str = Form("document"),
):
    ctx = None
    pipeline = None

    if mode == "document":
        ctx = PipelineContext(file=file)
        pipeline = DocumentPipeline()
    else:
        return {"error": "Unsupported mode"}

    result = await pipeline.run(ctx)

    print(result.pdf_bytes)
    return result
    # return StreamingResponse(
    #     io.BytesIO(result.pdf_bytes),
    #     media_type="application/pdf",
    #     headers={"Content-Disposition": "inline; filename=summary.pdf"}
    # )
