from fastapi import APIRouter, UploadFile, File, Form

router = APIRouter()

@router.post("/upload")
async def upload_document(
    title: str = Form(None),
    text: str = Form(None),
    file: UploadFile = File(None),
):
    if file:
        content = await file.read()
        return {
            "filename": file.filename,
            "size": len(content),
            "title": title
        }

    if text:
        return {
            "message": "Text received",
            "length": len(text)
        }

    return {"error": "No input"}
