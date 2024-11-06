import jwt
from typing import Union, Any
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from src.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PATH_PREFIX}/auth/login")


def verify_password(plain_password: str, hashed_password: str)-> bool:
    """
    Compares provided palin password with a stored hashed password.
    Args:
        plain_password: str
        hashed_password: str

    Returns:
        bool
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Creates a bcrypt hashed password.
    Args:
        password: str

    Returns:
        hashed_password: str
    """
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    Args:
        subject: str/Any
        expires_delta: tomedelta

    Returns:
        str
    """
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=5)

    to_encode = {"exp": expires, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT refresh token.
    Args:
        subject: str/Any
        expires_delta: tomedelta

    Returns:
        str
    """
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    to_encode = {"exp": expires, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt
    