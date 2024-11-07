import fastapi
from datetime import timedelta, datetime, timezone
from typing import Union, List, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from .service import UserService
from .schemas import UserSignUp, UserExist, User, Token, UserLogin
from .utils import (create_access_token, create_refresh_token,)
from .dependencies import AccessTokenBearer, RefreshTokenBearer, get_current_active_user
from src.config import settings


auth_router = fastapi.APIRouter(prefix="/auth")
access_token_bearer: AccessTokenBearer = AccessTokenBearer()
refresh_token_bearer: RefreshTokenBearer = RefreshTokenBearer()


@auth_router.post("/signup", response_model=Union[User,UserExist], status_code=status.HTTP_201_CREATED)
async def user_sign_up(user: UserSignUp, session: AsyncSession = Depends(get_async_session)):
    results = await UserService(session).create_user(user)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user sign up has failed, try again")
    if isinstance(results, UserExist):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results.model_dump())
    return results

@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def user_login(login_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    results = await UserService(session).authenticate_user(username=login_data.username, password=login_data.password)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return Token(
        access_token=create_access_token(results.username, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        refresh_token=create_refresh_token(results.username, expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES), refresh=True),
        token_type="bearer"
    )

@auth_router.get("/logout")
async def revoke_token(
    token_details=Depends(access_token_bearer)
):
    expiry_time = token_details.get("exp")
    user_name = token_details.get("sub")
    if not expiry_time or not user_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid or expired token"
        )
    
    return JSONResponse(content={"message": "logged out functionality coming soon"}, status_code=status.HTTP_200_OK)

@auth_router.get("/refresh_token", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    token_details=Depends(refresh_token_bearer)
):
    expiry_time = token_details.get("exp")
    user_name = token_details.get("sub")
    if not expiry_time or not user_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid or expired token"
        )
    if datetime.fromtimestamp(expiry_time).replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
        new_access_token = create_access_token(user_name, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        return JSONResponse(content={"access_token": new_access_token})
    
    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid or expired token"
    )

@auth_router.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
async def read_users(
    offset: int = 0, 
    limit: int = 100, 
    session: AsyncSession = Depends(get_async_session),
    _ = Depends(access_token_bearer)
):
    return await UserService(session).get_users(offset=offset, limit=limit)

@auth_router.get("/users/profile", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_profile(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
