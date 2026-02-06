from app.pipelines.steps.ingest_parse import ingest_parse_step
from app.pipelines.steps.structured_extract import structured_extract_step
from app.pipelines.steps.store_results import store_results_step
from app.pipelines.context import PipelineContext


class IngestionPipeline:
    def __init__(self):
        self.steps = [
            ingest_parse_step,
            structured_extract_step,
            store_results_step,
        ]

    async def run(self, ctx: PipelineContext) -> PipelineContext:
        for step in self.steps:
            result = step(ctx)
            if hasattr(result, "__await__"):
                ctx = await result
            else:
                ctx = result
        return ctx
