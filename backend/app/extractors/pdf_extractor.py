from __future__ import annotations

from typing import List

import os

from langchain_community.document_loaders import UnstructuredPDFLoader
from markdownify import markdownify as html_to_md
from app.utils.settings import settings


def _element_to_markdown(doc) -> str:
    text = (doc.page_content or "").strip()
    if not text:
        return ""

    category = (doc.metadata or {}).get("category", "")

    if category == "Title":
        depth = (doc.metadata or {}).get("category_depth", 1)
        try:
            depth = int(depth)
        except (TypeError, ValueError):
            depth = 1
        depth = max(1, min(depth, 4))
        return f"{'#' * depth} {text}"

    if category == "ListItem":
        return f"- {text}"

    if category == "Table":
        html = (doc.metadata or {}).get("text_as_html")
        if html:
            return html_to_md(html, heading_style="ATX")

    return text


def extract_pdf_markdown(file_path: str) -> str:
    if settings.poppler_path:
        # Ensure pdfinfo is discoverable even if PATH is not updated
        os.environ["PATH"] = f"{settings.poppler_path};{os.environ.get('PATH', '')}"
    if settings.tesseract_path:
        os.environ["TESSERACT_PATH"] = settings.tesseract_path
        os.environ["TESSERACT_CMD"] = settings.tesseract_path
        tesseract_dir = os.path.dirname(settings.tesseract_path)
        if tesseract_dir:
            os.environ["PATH"] = f"{tesseract_dir};{os.environ.get('PATH', '')}"
    if settings.ocr_agent:
        os.environ["OCR_AGENT"] = settings.ocr_agent
    loader = UnstructuredPDFLoader(
        file_path,
        mode="elements",
        strategy="hi_res",
        infer_table_structure=True,
        poppler_path=settings.poppler_path,
    )
    docs = loader.load()

    sections: List[str] = []
    for doc in docs:
        md = _element_to_markdown(doc)
        if md:
            sections.append(md)

    return "\n\n".join(sections).strip()
