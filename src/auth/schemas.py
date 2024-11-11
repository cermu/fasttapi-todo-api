import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    password: str


class UserSignUp(UserBase):
    email: EmailStr
    first_name: str
    last_name: str


class UserLogin(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserExist(BaseModel):
    message: str
    status: str


class User(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserSignUpResponse(BaseModel):
    message: str
    user: User


class EmailModel(BaseModel):
    addresses: List[str]
