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


class AdminSignUp(UserSignUp):
    role: str = "admin"
    is_verified: bool = True

class UserLogin(UserBase):
    pass


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserExist(BaseModel):
    message: str
    error_code: str


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
        from_attributes = True


class UserSignUpResponse(BaseModel):
    message: str
    user: User


class EmailModel(BaseModel):
    addresses: List[str]


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    new_password: str
    confirm_new_paddword: str
