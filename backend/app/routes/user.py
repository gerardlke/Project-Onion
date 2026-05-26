from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.db.session import get_db
from app.db.operation import (
    create_user,
    get_user_by_username,
)
from app.schemas.user import (
    CreateUserRequest,
    LoginRequest,
    UserResponse,
)


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()

@router.post("/create", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db)
):
    """API Route for creating a new user

    Input:

    Ouput:
    """
    existing_user = get_user_by_username(
        db,
        request.username
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = create_user(
        db,
        request.username
    )
    logger.info(f"Created new user with username {user.username}")
    return UserResponse(
        id=user.id,
        username=user.username
    )


@router.post("/login", response_model=UserResponse)
async def login_route(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """API Route for log in a user

    Input:

    Ouput:
    """
    user = get_user_by_username(
        db,
        request.username
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    logger.info(f"Found user with username {user.username}")
    return UserResponse(
        id=user.id,
        username=user.username
    )