from __future__ import annotations

from typing import List, Tuple
import os
import uuid

from langchain_core.documents import Document

from app.pipelines.context import PipelineContext
from app.services.postgres_service import get_connection, ensure_schema, insert_document
from app.services.chroma_service import store_documents
from app.services.neo4j_service import upsert_graph, upsert_custom_document


def _resolve_custom_doc_meta(ctx: PipelineContext, extraction: dict) -> Tuple[str, str, str]:
    doc_id = extraction.get("document_id") or extraction.get("id")
    if isinstance(doc_id, str) and doc_id.strip().lower() in ("null", "n/a", "-", ""):
        doc_id = None
    if not doc_id:
        doc_id = str(uuid.uuid4())

    title = extraction.get("document_title") or extraction.get("title")
    if isinstance(title, str) and title.strip().lower() in ("null", "n/a", "-", ""):
        title = None
    if not title:
        if ctx.file and getattr(ctx.file, "filename", None):
            title = os.path.splitext(ctx.file.filename)[0]
        elif ctx.source_path:
            title = os.path.splitext(os.path.basename(ctx.source_path))[0]
        elif ctx.text:
            title = ctx.text.strip().split("\n")[0][:40]
        else:
            title = "未命名文件"

    doc_type = extraction.get("document_type") or ctx.source_type or "custom"
    return doc_id, title, doc_type


def _build_vector_documents(ctx: PipelineContext) -> List[Document]:
    extraction = ctx.extraction
    if not extraction:
        return []

    if hasattr(extraction, "document_metadata"):
        doc = extraction.document_metadata
        summary = extraction.summary
        risk_level = extraction.risk_level
        decision_background = extraction.decision_background
        key_clauses = extraction.key_clauses
        risks = extraction.risks
        affected_components = extraction.affected_components
        entities = extraction.entities
    else:
        doc_id, doc_title, doc_type = _resolve_custom_doc_meta(ctx, extraction)
        extraction["document_id"] = doc_id
        extraction["document_title"] = doc_title
        extraction["document_type"] = doc_type
        doc = type("Doc", (), {
            "document_id": doc_id,
            "document_title": doc_title,
            "document_type": doc_type,
        })()
        summary = extraction.get("summary")
        risk_level = extraction.get("risk_level")
        decision_background = extraction.get("decision_background", [])
        key_clauses = extraction.get("key_clauses", [])
        risks = extraction.get("risks", [])
        affected_components = extraction.get("affected_components", [])
        entities = extraction.get("entities", [])

    parts = [
        f"Title: {doc.document_title}",
        f"Type: {doc.document_type}",
        f"Summary: {summary}",
    ]

    if decision_background:
        parts.append("Decision Background:")
        parts.extend([f"- {item}" for item in decision_background])

    if key_clauses:
        parts.append("Key Clauses:")
        parts.extend([f"- {item}" for item in key_clauses])

    if risks:
        parts.append("Risks:")
        parts.extend([f"- {item}" for item in risks])

    if affected_components:
        parts.append("Affected Components:")
        parts.extend([f"- {item}" for item in affected_components])

    if entities:
        parts.append("Entities:")
        # entities might be dicts if custom schema
        for e in entities:
            if hasattr(e, "name"):
                parts.append(f"- {e.name} ({e.type})")
            elif isinstance(e, dict):
                parts.append(f"- {e.get('name')} ({e.get('type')})")

    content = "\n".join([p for p in parts if p])

    metadata = {
        "document_id": doc.document_id,
        "document_title": doc.document_title,
        "document_type": doc.document_type,
        "source_type": ctx.source_type,
    }

    return [Document(page_content=content, metadata=metadata)]


async def store_results_step(ctx: PipelineContext) -> PipelineContext:
    if not ctx.extraction:
        raise ValueError("No extraction result to store")

    extraction = ctx.extraction
    is_default_schema = hasattr(extraction, "document_metadata")
    doc = extraction.document_metadata if is_default_schema else None

    conn = get_connection()
    schema = ensure_schema(conn, ctx.tenant_id)
    if is_default_schema:
        # Fill missing metadata from file/text to avoid unnamed documents
        if not doc.document_id or doc.document_id in ("N/A", "-", "null"):
            doc.document_id = str(uuid.uuid4())
        if not doc.document_title or doc.document_title in ("N/A", "-", "null"):
            if ctx.file and getattr(ctx.file, "filename", None):
                doc.document_title = os.path.splitext(ctx.file.filename)[0]
            elif ctx.source_path:
                doc.document_title = os.path.splitext(os.path.basename(ctx.source_path))[0]
            elif ctx.text:
                doc.document_title = ctx.text.strip().split("\n")[0][:40]
            else:
                doc.document_title = "未命名文件"
        insert_document(
            conn,
            schema,
            {
                "document_id": doc.document_id,
                "document_title": doc.document_title,
                "document_type": doc.document_type,
                "summary": extraction.summary,
                "risk_level": extraction.risk_level,
                "source": doc.source,
                "source_path": ctx.source_path,
                "raw_json": extraction.model_dump(mode="json"),
            },
        )
    else:
        doc_id, doc_title, doc_type = _resolve_custom_doc_meta(ctx, extraction)
        extraction["document_id"] = doc_id
        extraction["document_title"] = doc_title
        extraction["document_type"] = doc_type
        insert_document(
            conn,
            schema,
            {
                "document_id": doc_id,
                "document_title": doc_title,
                "document_type": doc_type,
                "summary": extraction.get("summary"),
                "risk_level": extraction.get("risk_level"),
                "source": ctx.file.filename if ctx.file else None,
                "source_path": ctx.source_path,
                "raw_json": extraction,
            },
        )
    conn.close()

    chroma_ok = True
    vector_docs = _build_vector_documents(ctx)
    try:
        store_documents(ctx.tenant_id, vector_docs)
    except Exception as exc:
        chroma_ok = False
        print(f"[WARN] Chroma storage skipped: {exc}")

    if is_default_schema:
        upsert_graph(ctx.tenant_id, extraction, ifc_components=ctx.ifc_components)
    else:
        upsert_custom_document(ctx.tenant_id, extraction)

    ctx.storage_result = {
        "postgres": True,
        "chroma": chroma_ok,
        "neo4j": True,
    }
    return ctx
