import time
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter, 
    UploadFile, 
    HTTPException, 
    Body,
    File, 
    Depends
)

from app.logging import setup_logger
from app.schemas.user import UserResponse as User
from app.schemas.upload import (
    UploadResponse,
    NewTopicResponse,
    GetTopicResponse
)
from app.db.session import get_db
from app.db.operations import (
    create_topic,
    get_all_topics_by_user_id
)
from app.pipelines.authentication_pipeline import get_current_user
from app.pipelines.upload_pipeline import process_document


### Set up configs
from app.configs.config import (
    ALLOWED_FILE_TYPES,
    MAX_FILE_SIZE_MB,
)


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()


@router.post("/new_topic", response_model=NewTopicResponse)
async def upload_topic(
    name: str = Body(...),
    description: str = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for creating a new topic of study for selection when uploading notes

    Input:

    Ouput:
    """
    try:
        new_topic = create_topic(db, user["id"], name, description)
        logger.info(f"Created new topic '{name}'")

        # Response model
        return NewTopicResponse(
            success=True,
            name=new_topic["name"],
            description=new_topic["description"]
        )

    except HTTPException as http_error:
        logger.warning(
            f"HTTP error: {http_error.detail}"
        )
        raise http_error

    except Exception as error:
        logger.exception(
            f"Unexpected error while creating new topic '{name}' due to {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/get_topics", response_model=GetTopicResponse)
async def get_all_topics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for retrieving all topics inserted by user for selection during file upload

    Input:

    Ouput:
    """
    try:
        all_topics = get_all_topics_by_user_id(
            db=db,
            user_id=user.id
        )
        logger.info(f"Retrieved {len(all_topics)} topic(s)")

        # Response model
        return GetTopicResponse(
            success=True,
            topics=all_topics
        )

    except HTTPException as http_error:
        logger.warning(
            f"HTTP error: {http_error.detail}"
        )
        raise http_error

    except Exception as error:
        logger.exception(
            f"Unexpected error while retrieving all topics due to {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/new_document", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    topic_name: str = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for uploading new document

    Input:

    Ouput:
    """
    try:
        logger.info(f"Upload request received for {file.filename}")
        logger.info("Starting file validation")
        start = time.time()

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
        logger.info("Starting file processing")
        metadata = await process_document(
            db=db,
            user=user,
            file=file,
            topic_name=topic_name
        )

        logger.info(f"Finished file upload in {round(time.time() - start)}s")

        # Response model
        return UploadResponse(
            success=True,
            topic=topic_name,
            filename=file.filename,
            content_type=file.content_type,
            size_mb=file.size,
            document_id=metadata.get("id", -1),
            num_chunks=metadata.get("num_chunks", -1),
            concepts=metadata.get("concepts", [])
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