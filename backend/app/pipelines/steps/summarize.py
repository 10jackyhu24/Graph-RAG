from app.transformers.summarizer import summarize
from app.pipelines.context import PipelineContext

async def summarize_step(ctx: PipelineContext):
    ctx.summary = await summarize(ctx.raw_text)
    return ctx
