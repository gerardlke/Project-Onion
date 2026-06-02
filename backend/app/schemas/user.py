from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class NewUserResponse(BaseModel):
    id: int
    username: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str