import time
import asyncio
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter, 
    UploadFile, 
    HTTPException, 
    BackgroundTasks,
    Body,
    File, 
    Depends
)
from fastapi.responses import StreamingResponse

from app.logging import setup_logger
from app.schemas.user import UserResponse as User
from app.schemas.upload import (
    NewTopicResponse,
    GetTopicResponse
)
from app.services.progress import ProgressTracker
from app.db.session import get_db
from app.db.operations import (
    create_topic,
    get_all_topics_by_user_id
)
from app.pipelines.authentication_pipeline import get_current_user
from app.pipelines.upload_pipeline import process_document

### Set up configs
from app.configs.config import SUPPORTED_EXTENSIONS

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
            user_id=user["id"]
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


@router.post("/new_document")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    topic_name: str = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for uploading new document and streams progress via SSE

    Input:

    Ouput:
    """
    # Validate extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file_extension} - Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Run pipeline
    logger.info(f"Upload request received for {file.filename}")
    tracker = ProgressTracker()

    async def run_and_stream():
        """Run pipeline concurrently with streaming progress updates"""
        start = time.time()

        pipeline_task = asyncio.create_task(
            process_document(
                db=db,
                user=user,
                file=file,
                topic_name=topic_name,
                background_tasks=background_tasks,
                tracker=tracker,
            )
        )

        # Stream SSE messages as pipeline posts them to tracker queue
        async for event in tracker.stream():
            yield event

        # Ensure pipeline exception surfaces
        try:
            await pipeline_task
        except Exception as e:
            logger.exception(f"Pipeline task failed for {file.filename}: {e}")

        logger.info(f"Upload stream complete in {round(time.time() - start)}s")

    return StreamingResponse(
        run_and_stream(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",  # Prevent Nginx/proxy buffering
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",  # Required for CORS
        }
    )