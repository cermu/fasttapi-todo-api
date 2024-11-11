import fastapi
from datetime import timedelta, datetime, timezone
from typing import Union, List, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from .service import UserService
from .schemas import UserSignUp, UserExist, User, Token, UserLogin, EmailModel, UserSignUpResponse
from .utils import (create_access_token, create_refresh_token, create_url_safe_token, decode_url_safe_token,)
from .dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker
from src.config import settings
from mail import create_message


auth_router = fastapi.APIRouter(prefix="/auth")
access_token_bearer: AccessTokenBearer = AccessTokenBearer()
refresh_token_bearer: RefreshTokenBearer = RefreshTokenBearer()


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    html = "<h1>Welcome to ToDO API</h1>"
    subject="Welcome"

    message = create_message(recipients=emails, subject=subject, body=html)
    return {"message": "email sent successfully", "content": message}

@auth_router.post("/signup", response_model=Union[UserSignUpResponse, UserExist], status_code=status.HTTP_201_CREATED)
async def user_sign_up(user: UserSignUp, session: AsyncSession = Depends(get_async_session)):
    results = await UserService(session).create_user(user)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user sign up has failed, try again")
    if isinstance(results, UserExist):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results.model_dump())
    
    token = create_url_safe_token({"email": user.email})
    link = f"http://{settings.API_BASE_URL}{settings.API_PATH_PREFIX}/auth/verify/{token}"
    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">linkk</a> to verify your email.</p>
    """

    message = create_message(recipients=[user.email], subject="Verify Email", body=html_message)
    
    # this is to be sent to the user's email but I am logging it for now.
    print("===================================================")
    print(f"User sign up email verification message: {message}")
    print("===================================================")

    return {
        "message": "account created! Check email to verify your account.",
        "user": results
    }

@auth_router.get("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_usre_account(token: str, session: AsyncSession = Depends(get_async_session)):
    # http://localhost:8080/todo-api/v1/auth/verify/eyJlbWFpbCI6InlvbW90aTM0NThAYW55cG5nLmNvbSJ9.ZzIAqw.-zWLwO7gx7v4hRx_X3aO4Kb8FzE
    token_data = decode_url_safe_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="invalid verification token"
        )
    
    user_email = token_data.get("email")

    if user_email:
        user = await UserService(session).get_user_by_email(user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="user not found"
            )
        await UserService(session).update_user(user, {"is_verified": True})
        return JSONResponse(
            content={"message": "account verified successfully"}
        )
    return JSONResponse(
        content={"message": "account verification failed."},
        status_code=status.HTTP_400_BAD_REQUEST
    )

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
    _ = Depends(access_token_bearer),
    allowed_admin: User = Depends(RoleChecker(["admin"]))
):
    return await UserService(session).get_users(offset=offset, limit=limit)

@auth_router.get("/users/profile", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_profile(current_user: Annotated[User, Depends(RoleChecker(["admin", "user"]))]):
    return current_user
