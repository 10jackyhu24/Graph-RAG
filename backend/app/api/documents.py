from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

from app.services.postgres_service import (
    get_connection,
    ensure_schema,
    list_documents,
    get_document,
    get_document_by_row_id,
    delete_document,
    delete_document_by_row_id,
)
from app.services.chroma_service import delete_documents_by_id
from app.services.neo4j_service import delete_document as delete_graph_document

router = APIRouter()


@router.get("/documents")
def list_docs(tenant_id: str, limit: int = 20):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    docs = list_documents(conn, schema, limit=limit)
    conn.close()
    return docs


@router.get("/documents/{document_id}/download")
def download_doc(document_id: str, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    doc = get_document(conn, schema, document_id)
    conn.close()
    if not doc or not doc.get("source_path"):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(doc["source_path"], filename=doc.get("source") or "document")


@router.get("/documents/by-row/{row_id}/download")
def download_doc_by_row(row_id: int, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    doc = get_document_by_row_id(conn, schema, row_id)
    conn.close()
    if not doc or not doc.get("source_path"):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(doc["source_path"], filename=doc.get("source") or "document")


@router.get("/documents/{document_id}")
def get_doc_detail(document_id: str, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    doc = get_document(conn, schema, document_id)
    conn.close()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/documents/by-row/{row_id}")
def get_doc_detail_by_row(row_id: int, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    doc = get_document_by_row_id(conn, schema, row_id)
    conn.close()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/documents/{document_id}")
def delete_doc(document_id: str, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    doc = get_document(conn, schema, document_id)
    delete_document(conn, schema, document_id)
    conn.close()
    delete_documents_by_id(tenant_id, document_id)
    delete_graph_document(tenant_id, document_id)
    if doc and doc.get("source_path"):
        try:
            import os
            if os.path.exists(doc["source_path"]):
                os.remove(doc["source_path"])
        except Exception:
            pass
    return {"status": "ok", "deleted": doc.get("source_path") if doc else None}


@router.delete("/documents/by-row/{row_id}")
def delete_doc_by_row(row_id: int, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    doc = get_document_by_row_id(conn, schema, row_id)
    delete_document_by_row_id(conn, schema, row_id)
    conn.close()
    if doc and doc.get("document_id"):
        delete_documents_by_id(tenant_id, doc["document_id"])
        delete_graph_document(tenant_id, doc["document_id"])
    if doc and doc.get("source_path"):
        try:
            import os
            if os.path.exists(doc["source_path"]):
                os.remove(doc["source_path"])
        except Exception:
            pass
    return {"status": "ok", "deleted": doc.get("source_path") if doc else None}
