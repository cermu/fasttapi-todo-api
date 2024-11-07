from typing import Annotated
from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from .service import UserService
from .models import User
from .utils import decode_token


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = self.token_valid(token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="invalid or expired token"
            )
        if token_data.get("error"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=token_data.get("error")
            )
        
        self.verify_token_data(token_data)
        return token_data
    
    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return token_data
    
    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide an access token"
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide a refresh token"
            )


async def get_current_user(
        token_details: Annotated[dict, Depends(AccessTokenBearer())],
        session: AsyncSession = Depends(get_async_session)
):
    """
    Get the current authenticated user making a request.
    Args:
        token: str
        session: AsyncSession

    Returns:
        A user: User
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    username: str = token_details.get("sub")
    if not username:
        raise credentials_exception
    
    user = await UserService(session).get_user_by_username(username=username)
    if not user:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get the current active authenticated user making a request.
    Args:
        current_user: User

    Returns:
        A user: User
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="user is inactive"
        )
    return current_user
