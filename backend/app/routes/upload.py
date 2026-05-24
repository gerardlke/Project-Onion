from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter, 
    UploadFile, 
    HTTPException, 
    File, 
    Depends
)

from app.logging import setup_logger
from app.pipelines.upload_pipeline import process_document
from app.schemas.upload import UploadResponse
from app.db.session import get_db


### Set up configs
from app.configs.config import (
    ALLOWED_FILE_TYPES,
    MAX_FILE_SIZE_MB,
)


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """API Route for uploading new document

    Input:

    Ouput:
    """
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
        metadata = await process_document(
            file=file,
            db=db
        )

        logger.info("Finished file upload.")

        # Response model
        return UploadResponse(
            success=True,
            filename=file.filename,
            content_type=file.content_type,
            size_mb=file.size,
            document_id=metadata.get("id", -1),
            num_chunks=metadata.get("chunks", -1),
            num_concepts=metadata.get("concepts", -1)
        )

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