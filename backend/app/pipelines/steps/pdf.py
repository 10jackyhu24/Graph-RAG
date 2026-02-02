from app.services.pdf_service import summary_to_pdf
from app.pipelines.context import PipelineContext

def pdf_step(ctx: PipelineContext):
    ctx.pdf_bytes = summary_to_pdf(ctx.summary)
    return ctx