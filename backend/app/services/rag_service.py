from __future__ import annotations

import json
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate

from app.services.chroma_service import get_vector_store
from app.services.llm_router import get_llm
from app.services.postgres_service import get_connection, ensure_schema, list_documents
from app.services.neo4j_service import _tenant_label, get_driver


RAG_SYSTEM = """
You are a helpful industrial knowledge assistant. Use the provided context from
vector search, documents, and graph relations to answer the question.
If you are unsure, say you need more documents.
""".strip()


def build_rag_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM),
            (
                "human",
                "Question:\n{question}\n\nContext:\n{context}\n\nAnswer in the requested language: {language}. Use Traditional Chinese when Chinese is requested.",
            ),
        ]
    )


def _collect_graph_context(tenant_id: str, limit: int = 20) -> str:
    label = _tenant_label(tenant_id)
    driver = get_driver()
    lines = []
    with driver.session() as session:
        result = session.run(
            f"""
            MATCH (d:Document:{label})-[r]->(e)
            RETURN d.document_id AS doc_id, d.title AS title, type(r) AS rel, e.name AS name
            LIMIT $limit
            """,
            limit=limit,
        )
        for record in result:
            lines.append(
                f"Doc {record['doc_id']} ({record['title']}): {record['rel']} -> {record['name']}"
            )
    driver.close()
    return "\n".join(lines)


def _collect_vector_context(tenant_id: str, query: str, k: int = 4) -> str:
    try:
        store = get_vector_store(tenant_id)
        docs = store.similarity_search(query, k=k)
    except Exception:
        return ""
    chunks = []
    for doc in docs:
        chunks.append(doc.page_content)
    return "\n\n".join(chunks)


def _collect_documents_context(tenant_id: str, limit: int = 5) -> str:
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    docs = list_documents(conn, schema, limit=limit)
    conn.close()
    lines = []
    for d in docs:
        lines.append(
            f"{d.get('document_id')} | {d.get('document_title')} | {d.get('summary')}"
        )
    return "\n".join(lines)


def build_context(tenant_id: str, query: str) -> str:
    vector_ctx = _collect_vector_context(tenant_id, query)
    doc_ctx = _collect_documents_context(tenant_id)
    graph_ctx = _collect_graph_context(tenant_id)

    parts = []
    if vector_ctx:
        parts.append("[Vector]\n" + vector_ctx)
    if doc_ctx:
        parts.append("[Documents]\n" + doc_ctx)
    if graph_ctx:
        parts.append("[Graph]\n" + graph_ctx)
    return "\n\n".join(parts)


async def stream_rag_answer(
    tenant_id: str,
    question: str,
    language: str,
    provider: Optional[str],
    model: Optional[str],
):
    llm = get_llm(provider=provider, model=model, temperature=0)
    context = build_context(tenant_id, question)
    prompt = build_rag_prompt()
    chain = prompt | llm
    language = _normalize_language(language)

    async for chunk in chain.astream({
        "question": question,
        "context": context,
        "language": language,
    }):
        content = chunk.content if hasattr(chunk, "content") else str(chunk)
        if content:
            yield content


def _normalize_language(language: str) -> str:
    if not language:
        return "zh-Hant"
    lower = language.lower().replace("_", "-")
    if lower in ("zh", "zh-hant", "zh-tw", "zh-hk"):
        return "zh-Hant"
    return language
