from app.services.pdf_service import decision_to_view
from app.pipelines.context import PipelineContext

def pdf_step(ctx: PipelineContext):
    ctx.pdf_json = decision_to_view(ctx.summary)
    return ctx