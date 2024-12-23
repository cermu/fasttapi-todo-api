import jwt
import uuid
from jwt.exceptions import PyJWTError
from typing import Union, Any
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from src.utils.config import settings
from src.utils.celery_tasks import send_email


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

def create_access_token(subject: Union[str, Any], expires_delta: timedelta | None = None, refresh: bool = False) -> str:
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

    to_encode = {"token_id": str(uuid.uuid4()), "exp": expires, "sub": str(subject), "refresh": refresh}
    encoded_jwt = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta | None = None, refresh: bool = True) -> str:
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

    to_encode = {"token_id": str(uuid.uuid4()), "exp": expires, "sub": str(subject), "refresh": refresh}
    encoded_jwt = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        token_data = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return token_data
    except PyJWTError as e:
        error_data = {"error": str(e)}
        return error_data
    
serializer = URLSafeTimedSerializer(
    secret_key=settings.SECRET_KEY,
    salt="email-verification"
)

def create_url_safe_token(data: dict):
    return serializer.dumps(data)

def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        return {"error": str(e)}

def send_user_verification_email(email: str):
    token = create_url_safe_token({"email": email})
    link = f"http://{settings.API_BASE_URL}{settings.API_PATH_PREFIX}/auth/users/verify/{token}"
    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email.</p>
    """
    subject = "Verify Email"
    
    send_email.delay([email], subject, html_message)

def send_password_reset_email(email: str):
    token = create_url_safe_token({"email": email})
    link = f"http://{settings.API_BASE_URL}{settings.API_PATH_PREFIX}/auth/users/password-reset-confirm/{token}"
    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to reset your password.</p>
    """
    subject = "Password Reset Request"
    
    send_email.delay([email], subject, html_message)
