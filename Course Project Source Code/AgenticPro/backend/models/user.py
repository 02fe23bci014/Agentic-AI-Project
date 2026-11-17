from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    username: str
    role: str # "student" | "faculty"
    full_name: str
    email: str | None = None


class UserLoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str = "student" # "student" | "faculty"


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=4)
    role: str = "student" # "student" | "faculty"
    full_name: str = Field(min_length=1)
    email: str | None = None


class UserUpdateRequest(BaseModel):
    user_id: str = Field(min_length=1)
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
