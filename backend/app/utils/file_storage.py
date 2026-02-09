from __future__ import annotations

import os
import uuid
from fastapi import UploadFile

from app.utils.settings import settings


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


async def save_upload_file(upload_file: UploadFile) -> str:
    uploads_dir = os.path.join(settings.data_dir, "uploads")
    ensure_dir(uploads_dir)

    safe_name = upload_file.filename.replace(" ", "_")
    file_id = uuid.uuid4().hex
    file_path = os.path.join(uploads_dir, f"{file_id}_{safe_name}")

    content = await upload_file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return file_path
