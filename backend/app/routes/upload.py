import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import (
    UPLOAD_DIR,
    ALLOWED_FILE_TYPES,
    MAX_FILE_SIZE_MB,
)

router = APIRouter()


@router.post("/")
async def upload_document(file: UploadFile = File(...)):

    # Validate extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}"
        )

    # Validate size
    file_contents = await file.read()

    file_size_mb = len(file_contents) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit"
        )

    # Save file
    save_path = UPLOAD_DIR / file.filename

    with open(save_path, "wb") as buffer:
        buffer.write(file_contents)

    # Response
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_mb": round(file_size_mb, 2),
        "saved_to": str(save_path),
        "status": "uploaded"
    }