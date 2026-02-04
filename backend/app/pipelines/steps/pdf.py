from app.services.pdf_service import decision_pdf
from app.pipelines.context import PipelineContext

def pdf_step(ctx: PipelineContext):
    ctx.pdf_json = decision_pdf(ctx.summary)
    return ctx