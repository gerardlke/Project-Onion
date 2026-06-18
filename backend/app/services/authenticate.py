import os
import jwt
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone


# Set up configs
load_dotenv()


def hash_password(password: str) -> str:
    """Helper function to hash password 

    Input:

    Ouput:
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Helper function to verify password against hashed password

    Input:

    Ouput:
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user_id: int):
    """Helper funciton to create access token for subsequent API requests

    Input:

    Ouput:
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES", 60)))

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM")
    )
