import os
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.services.authenticate import (
    hash_password,
    verify_password,
    create_access_token    
)
from app.db.session import get_db
from app.db.operations import (
    create_user,
    get_user_by_username
)
from app.schemas.user import (
    CreateUserRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
from app.logging import setup_logger


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()

@router.post("/create", response_model=UserResponse)
async def create_user_request(
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

    hashed_password = hash_password(request.password)

    user = create_user(
        db,
        request.username,
        hashed_password
    )   
    logger.info(f"Created new user with username {request.username}")

    return UserResponse(
        id=user["id"],
        username=user["username"]
    )


@router.post("/login", response_model=TokenResponse)
async def login_route(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """API Route for logging in a user

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

    user = user[0]

    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password entered"
        )
    logger.info(f"User '{request.username}' verified")

    access_token = create_access_token(user["id"])
    logger.info(f"Authentication token for '{request.username}' created")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        id=user["id"],
        username=user["username"]
    )