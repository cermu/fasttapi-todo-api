import fastapi
import jwt
from datetime import timedelta
from jwt.exceptions import InvalidTokenError
from typing import Union, List, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from .service import UserService
from .schemas import UserSignUp, UserExist, User, Token, TokenData
from src.auth.utils import (create_access_token, create_refresh_token, oauth2_scheme,)
from src.config import settings


auth_router = fastapi.APIRouter(prefix="/auth")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(get_async_session)):
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

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        credentials_exception.detail = str(e)
        raise credentials_exception
    user = await UserService(session).get_user_by_username(username=token_data.username)
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

@auth_router.post("/signup", response_model=Union[User,UserExist], status_code=status.HTTP_201_CREATED)
async def user_sign_up(user: UserSignUp, session: AsyncSession = Depends(get_async_session)):
    results = await UserService(session).create_user(user)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user sign up has failed, try again")
    if isinstance(results, UserExist):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results.model_dump())
    return results

@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    results = await UserService(session).authenticate_user(username=form_data.username, password=form_data.password)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return Token(
        access_token=create_access_token(results.username, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        refresh_token=create_refresh_token(results.username, expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)),
        token_type="bearer"
    )

@auth_router.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
async def read_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    offset: int = 0, 
    limit: int = 100, 
    session: AsyncSession = Depends(get_async_session)
    ):
    return await UserService(session).get_users(offset=offset, limit=limit)

@auth_router.get("/users/profile", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_profile(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
