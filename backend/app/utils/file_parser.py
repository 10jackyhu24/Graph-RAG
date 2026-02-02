from fastapi import UploadFile
import os
import io

from PyPDF2 import PdfReader
import docx


async def parse_file(file: UploadFile) -> str:
    """
    Parse the uploaded file and extract text content.
    Supports PDF, DOCX, and TXT files.
    Raises ValueError for unsupported file types.
    """

    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        return await _parse_pdf(file)

    elif filename.endswith(".docx"):
        return await _parse_docx(file)

    elif filename.endswith(".txt"):
        content = await file.read()
        return content.decode("utf-8")

    else:
        raise ValueError("Unsupported file type")


async def _parse_pdf(file: UploadFile) -> str:
    content = await file.read()
    reader = PdfReader(io.BytesIO(content))

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text


async def _parse_docx(file: UploadFile) -> str:
    content = await file.read()
    doc = docx.Document(io.BytesIO(content))

    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)
