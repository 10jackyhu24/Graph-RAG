from __future__ import annotations

import os
import docx

from app.extractors.pdf_extractor import extract_pdf_markdown
from app.extractors.ifc_extractor import extract_ifc_summary
from app.utils.file_storage import save_upload_file
from app.pipelines.context import PipelineContext


async def ingest_parse_step(ctx: PipelineContext) -> PipelineContext:
    if ctx.text:
        ctx.raw_text = ctx.text
        ctx.source_type = ctx.source_type or "text"
        return ctx

    if not ctx.file:
        raise ValueError("No input file or text provided")

    file_path = await save_upload_file(ctx.file)
    ctx.source_path = file_path
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    source_type = (ctx.source_type or ext).lower()
    ctx.source_type = source_type

    if source_type == "pdf":
        ctx.markdown = extract_pdf_markdown(file_path)
        ctx.raw_text = ctx.markdown
        return ctx

    if source_type in ("ifc", "ifczip"):
        result = extract_ifc_summary(file_path)
        ctx.ifc_components = result.components
        ctx.raw_text = result.summary
        return ctx

    if source_type == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            ctx.raw_text = f.read()
        return ctx

    if source_type == "docx":
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs]
        ctx.raw_text = "\n".join(paragraphs)
        return ctx

    raise ValueError(f"Unsupported file type: {ext}")
