from app.pipelines.steps.parse import parse_step
from app.pipelines.steps.summarize import summarize_step
from app.pipelines.steps.pdf import pdf_step
from app.pipelines.context import PipelineContext

class DocumentPipeline:
    def __init__(self):
        self.steps = [
            parse_step,
            summarize_step,
            pdf_step,
        ]

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        for step in self.steps:
            result = step(ctx)
            if hasattr(result, "__await__"):
                ctx = await result
            else:
                ctx = result
        return ctx
