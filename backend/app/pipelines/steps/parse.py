from app.utils.file_parser import parse_file
from app.pipelines.context import PipelineContext

async def parse_step(ctx: PipelineContext):
    if ctx.file:
        ctx.raw_text = await parse_file(ctx.file)
    return ctx
