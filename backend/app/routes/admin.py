import os
import secrets
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.operations import reset_database
from app.logging import setup_logger


### Set up API, logger, and security schemes
logger = setup_logger(__name__)
router = APIRouter()
security = HTTPBasic()

### Set up admin role
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Dependency function to validate admin access against basic auth headers.

    Input:

    Ouput:
    """
    correct_username = secrets.compare_digest(credentials.username, ADMIN_PASSWORD)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        logger.warning(f"Unauthorized admin access attempt by username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect administrative username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.post("/reset_db")
async def administrative_db_reset(
    db: Session = Depends(get_db),
    admin_user: str = Depends(verify_admin_credentials)  # Guarantees password check runs
):
    """API Route to clear all data rows from database

    Input:

    Ouput:
    """
    try:
        logger.warning(f"Admin user '{admin_user}' clearing database.")
        
        # Execute your reset operation function
        result = reset_database(db)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("detail", "Failed to clear data.")
            )
            
        logger.info("Database successfully cleared.")
        return {"status": "success", "message": "All concepts, documents, and users have been cleared."}
        
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        logger.exception(f"Unexpected crash during admin db reset sequence: {error}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while resetting database contents."
        )