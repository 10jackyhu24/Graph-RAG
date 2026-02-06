from __future__ import annotations

import os
import re
from typing import List
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings as ChromaSettings
try:
    from langchain_chroma import Chroma
except ImportError:  # fallback for older installs
    from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:  # fallback for older installs
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata

from app.utils.settings import settings


def _sanitize_identifier(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", value.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "default"


def _get_chroma_client():
    if not settings.chroma_http_url:
        return None
    parsed = urlparse(settings.chroma_http_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 8000
    return chromadb.HttpClient(host=host, port=port, settings=_get_client_settings())


def _get_client_settings():
    # Disable telemetry to avoid noisy errors in console.
    return ChromaSettings(anonymized_telemetry=False)


def get_embeddings():
    if settings.embeddings_provider == "disabled":
        raise RuntimeError("Embeddings disabled")
    if settings.embeddings_provider == "ollama":
        return OllamaEmbeddings(model="nomic-embed-text", base_url=settings.ollama_base_url)
    if settings.embeddings_provider == "sentence-transformers":
        return HuggingFaceEmbeddings(model_name=settings.st_embeddings_model)
    raise RuntimeError(f"Unsupported embeddings provider: {settings.embeddings_provider}")


def get_vector_store(tenant_id: str) -> Chroma:
    safe_tenant = _sanitize_identifier(tenant_id)
    collection = f"tenant_{safe_tenant}"
    client = _get_chroma_client()
    persist_dir = None

    if not client:
        persist_dir = os.path.join(settings.chroma_base_dir, safe_tenant)
        os.makedirs(persist_dir, exist_ok=True)

    return Chroma(
        collection_name=collection,
        embedding_function=get_embeddings(),
        persist_directory=persist_dir,
        client=client,
        client_settings=_get_client_settings(),
    )


def store_documents(tenant_id: str, documents: List[Document]) -> None:
    if not documents:
        return
    safe_docs = []
    for doc in documents:
        filtered = filter_complex_metadata(doc)
        # Drop None metadata values that Chroma rejects
        if filtered.metadata:
            filtered.metadata = {k: v for k, v in filtered.metadata.items() if v is not None}
        safe_docs.append(filtered)
    store = get_vector_store(tenant_id)
    store.add_documents(safe_docs)
    if not settings.chroma_http_url:
        store.persist()


def delete_documents_by_id(tenant_id: str, document_id: str) -> None:
    try:
        store = get_vector_store(tenant_id)
        store._collection.delete(where={"document_id": document_id})
    except Exception:
        return
