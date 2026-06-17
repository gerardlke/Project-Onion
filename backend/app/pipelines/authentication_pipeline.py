import os
import jwt
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.operations import get_user_by_id


### Set up 
load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Pipeline to authenticate requests via user

    Input:

    Ouput:
    """
    payload = jwt.decode(
        token,
        os.getenv("JWT_SECRET_KEY"),
        algorithms=[
            os.getenv("JWT_ALGORITHM")
        ]
    )
    user_id = payload["sub"]
    user = get_user_by_id(int(user_id))
    return user