import fastapi
from typing import Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from .service import UserService
from .schemas import UserSignUp, UserExist, User, Token
from src.auth.utils import create_access_token, create_refresh_token



auth_router = fastapi.APIRouter(prefix="/auth")


@auth_router.post("/signup", response_model=Union[User,UserExist], status_code=status.HTTP_201_CREATED)
async def user_sign_up(user: UserSignUp, session: AsyncSession = Depends(get_async_session)):
    results = await UserService(session).create_user(user)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user sign up has failed, try again")
    if isinstance(results, UserExist):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results.model_dump())
    return results

@auth_router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    results = await UserService(session).authenticate_user(username=form_data.username, password=form_data.password)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {
        "access_token": create_access_token(results.username), 
        "refresh_token": create_refresh_token(results.username), 
        "token_type": "bearer"
    }
