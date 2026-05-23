from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.logging import setup_logger
from app.pipelines.upload_pipeline import process_document
from app.schemas.upload import UploadResponse

### Set up configs
from app.config import (
    ALLOWED_FILE_TYPES,
    MAX_FILE_SIZE_MB,
)


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):

    try:
        logger.info(f"Upload request received for {file.filename}.")
        logger.info("Starting file validation.")

        # Validate extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {file_extension}"
            )

        # Validate size (without reading into memory)
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit"
            )

        # Run pipeline
        logger.info("Starting file processing.")
        processed = await process_document(
            file,
            filename=file.filename
        )

        logger.info("Finished file upload.")

        # Response
        return {
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_mb": round(file.size, 2),
            "concepts": processed.get("concepts", [])
        }

    except HTTPException as http_error:
        logger.warning(
            f"HTTP error: {http_error.detail}"
        )
        raise http_error

    except Exception as error:
        logger.exception(
            f"Unexpected error while processing {file.filename} due to {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )