from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.db.session import get_db
from app.pipelines.authentication_pipeline import get_current_user
from app.pipelines.chat_pipeline import process_chat_query
from app.schemas.user import UserResponse as User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)
from app.logging import setup_logger


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for RAG chat endpoint.

    Input: Accepts the user's query and full conversation history from the frontend
    
    Output: Returns LLM response and which concept nodes were used as context
    """
    try:
        logger.info(f"Chat query from user '{user["username"]}'")

        result = await process_chat_query(
            db=db,
            user_id=user["id"],
            query=request.query,
            conversation_history=[
                {"role": m.role, "content": m.content}
                for m in request.conversation_history
            ]
        )
        return ChatResponse(**result)

    except Exception as e:
        logger.exception(f"Chat query failed for user '{user["username"]}': {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )