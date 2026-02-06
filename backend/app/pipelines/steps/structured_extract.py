from __future__ import annotations

from app.pipelines.context import PipelineContext
from app.services.structured_extractor import extract_engineering_logic, extract_with_agent
from app.services.postgres_service import get_connection, ensure_schema, get_agent


async def structured_extract_step(ctx: PipelineContext) -> PipelineContext:
    if not ctx.raw_text:
        raise ValueError("No content to extract")

    agent = None
    if ctx.agent_id:
        conn = get_connection()
        schema = ensure_schema(conn, ctx.tenant_id)
        agent = get_agent(conn, schema, ctx.agent_id)
        conn.close()
        ctx.agent = agent

    if agent:
        ctx.extraction = await extract_with_agent(
            ctx.raw_text,
            agent=agent,
            provider=ctx.llm_provider,
            model=ctx.llm_model,
        )
    else:
        ctx.extraction = await extract_engineering_logic(
            ctx.raw_text,
            provider=ctx.llm_provider,
            model=ctx.llm_model,
        )
    if (
        ctx.file
        and ctx.extraction
        and hasattr(ctx.extraction, "document_metadata")
        and ctx.extraction.document_metadata.source is None
    ):
        ctx.extraction.document_metadata.source = ctx.file.filename
    return ctx
