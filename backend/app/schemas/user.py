from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str

class LoginRequest(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: int
    username: str