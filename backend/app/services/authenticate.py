import os
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext


# Set up configs
load_dotenv()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """Helper function to hash password 

    Input:

    Ouput:
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Helper function to verify password against hashed password

    Input:

    Ouput:
    """
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(user_id: int, timeout: int = 60):
    """Helper funciton to create access token for subsequent API requests

    Input:

    Ouput:
    """
    expire = datetime.utcnow() + timedelta(minutes=timeout)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
