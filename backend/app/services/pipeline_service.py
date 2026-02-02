from app.sources.document_source import DocumentSource
from app.pipelines.document_pipeline import DocumentPipeline

async def run_pipeline(mode, file):
    pipeline = None
    source = None

    if mode == "document":
        source = DocumentSource(file)
        pipeline = DocumentPipeline()

    data = await source.load()

    for step in pipeline.steps:
        data = step(data)

    return data
