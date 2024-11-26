from typing import Annotated, List, Any
from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from src.db.redis import is_token_id_in_blocklist
from .service import UserService
from .models import User
from .utils import decode_token
from src.utils.errors import (
    InvalidTokenException,
    RevokedTokenException,
    AccessTokenRequiredException,
    RefreshTokenRequiredException,
    InsufficientPermissionException,
    UnverifiedUserException,
    InactiveUSerException,
    InvalidTokenDataException,
)

user_service: UserService = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = self.token_valid(token)

        if not token_data:
            raise InvalidTokenException()
        if token_data.get("error"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=token_data.get("error")
            )
        is_token_id_in_blocklist_results = await is_token_id_in_blocklist(token_data.get("token_id"))
        if is_token_id_in_blocklist_results.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=is_token_id_in_blocklist_results.get("error")
            )
        
        if is_token_id_in_blocklist_results.get("results"):
            raise RevokedTokenException()
        
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
            raise AccessTokenRequiredException()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data.get("refresh"):
            raise RefreshTokenRequiredException()


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
    username: str = token_details.get("sub")
    if not username:
        raise InvalidTokenDataException()
    
    user = await user_service.get_user_by_username(session=session, username=username)
    if not user:
        raise InvalidTokenDataException()
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)], request: Request):
    """
    Get the current active authenticated user making a request.
    Args:
        current_user: User

    Returns:
        A user: User
    """
    request_url = str(request.url)
    if not current_user.is_active and "/auth/users/profile/activate" not in request_url:
        raise InactiveUSerException()
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> Any:
        if not current_user.is_verified:
            raise UnverifiedUserException()
        if current_user.role in self.allowed_roles:
            return current_user
        raise InsufficientPermissionException()
