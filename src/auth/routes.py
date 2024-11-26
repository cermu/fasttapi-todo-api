import fastapi
from datetime import timedelta, datetime, timezone
from typing import Union, List, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from src.db.redis import add_token_id_to_blocklist
from .service import UserService
from .schemas import (
    UserSignUp, UserExist, User, 
    Token, UserLogin, EmailModel, 
    UserSignUpResponse, PasswordResetRequest, PasswordResetConfirm,
    UserUpdate, AdminSignUp,
)
from .utils import (
    create_access_token, create_refresh_token, decode_url_safe_token, get_password_hash, send_user_verification_email, send_password_reset_email,
)
from .dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker
from src.utils.config import settings
from src.utils.celery_tasks import send_email
from src.utils.errors import (
    InvalidCredentialsException,
    InvalidTokenException,
    InvalidVerifyTokenDataException,
    ResourceNotFoundException,
    PasswordsMismatchException,
    UserInactiveOrNotFoundException,
    InternalServerErrorException,
)


auth_router = fastapi.APIRouter(prefix="/auth")
access_token_bearer: AccessTokenBearer = AccessTokenBearer()
refresh_token_bearer: RefreshTokenBearer = RefreshTokenBearer()
user_service: UserService = UserService()


@auth_router.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
async def read_users(
    offset: int = 0, 
    limit: int = 100, 
    session: AsyncSession = Depends(get_async_session),
    _ = Depends(access_token_bearer),
    allowed_admin: User = Depends(RoleChecker(["admin"]))
):
    return await user_service.get_users(session=session, offset=offset, limit=limit)

@auth_router.get("/users/profile", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_profile(current_user: Annotated[User, Depends(RoleChecker(["admin", "user"]))]):
    return current_user

@auth_router.get("/users/profile/deactivate", response_model=UserSignUpResponse, status_code=status.HTTP_200_OK)
async def deactivate_user_profile(current_user: Annotated[User, Depends(RoleChecker(["admin", "user"]))], token_details=Depends(access_token_bearer), session: AsyncSession = Depends(get_async_session)):
    results = await user_service.update_user(session=session, user=current_user, update_data={"is_active": False})
    token_id = token_details.get("token_id")
    token_blocked = await add_token_id_to_blocklist(token_id)
    
    if token_blocked.get("error"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "message": f"an error occurred while deactivating the user: {token_blocked.get("error")}",
                "error_code": "SE002"
            }
        )
    return {
            "message": "user has been deactivated successfully.",
            "user": results
        }

@auth_router.get("/users/profile/activate", response_model=UserSignUpResponse, status_code=status.HTTP_200_OK)
async def activate_user_profile(current_user: Annotated[User, Depends(RoleChecker(["admin", "user"]))], session: AsyncSession = Depends(get_async_session)):
    results = await user_service.update_user(session=session, user=current_user, update_data={"is_active": True})
    return {
            "message": "user has been activated successfully.",
            "user": results
        }

@auth_router.get("/users/logout")
async def revoke_token(
    token_details=Depends(access_token_bearer)
):
    token_id = token_details.get("token_id")
    token_blocked = await add_token_id_to_blocklist(token_id)
    
    if token_blocked.get("error"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "message": f"an error occurred while logging out the user: {token_blocked.get("error")}",
                "error_code": "SE002"
            }
        )
    return JSONResponse(content={"message": "logged out successfully"}, status_code=status.HTTP_200_OK)

@auth_router.get("/users/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    token_details=Depends(refresh_token_bearer)
):
    expiry_time = token_details.get("exp")
    user_name = token_details.get("sub")
    
    if not expiry_time or not user_name:
        raise InvalidTokenException()
    if datetime.fromtimestamp(expiry_time).replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
        new_access_token = create_access_token(user_name, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        return JSONResponse(content={"access_token": new_access_token})
    
    raise InvalidTokenException()

@auth_router.get("/users/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(id: str, _: Annotated[User, Depends(RoleChecker(["admin"]))], session: AsyncSession = Depends(get_async_session)):
    existing_user = await user_service.get_user_by_id(session=session, id=id)
    if not existing_user:
        raise ResourceNotFoundException()
    
    return existing_user

@auth_router.get("/users/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_user_account(token: str, session: AsyncSession = Depends(get_async_session)):
    token_data = decode_url_safe_token(token)
    if token_data is None:
        raise InvalidVerifyTokenDataException()
    
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(session=session, email=user_email)
        if not user:
            raise ResourceNotFoundException()
        await user_service.update_user(session=session, user=user, update_data={"is_verified": True})
        return JSONResponse(
            content={"message": "account verified successfully"}
        )
    return JSONResponse(
        content={"message": "account verification failed.", "error_code": "CE016"},
        status_code=status.HTTP_400_BAD_REQUEST
    )

@auth_router.post("/send-mail", status_code=status.HTTP_200_OK)
async def send_mail(emails: EmailModel):
    try:
        emails = emails.addresses
        html = "<h1>Welcome to ToDO API</h1>"
        subject="Welcome"
        send_email.delay(emails, subject, html)
        return {"message": "email sent successfully"}
    except Exception as e:
        print("===================================")
        print(f"Request processing error: {str(e)}")
        print("===================================")
        raise InternalServerErrorException()

@auth_router.post("/users/signup", response_model=Union[UserSignUpResponse, UserExist], status_code=status.HTTP_201_CREATED)
async def user_sign_up(user: UserSignUp, session: AsyncSession = Depends(get_async_session)):
    results = await user_service.create_user(session=session, user=user)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user sign up has failed, try again")
    if isinstance(results, UserExist):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results.model_dump())
    
    send_user_verification_email(email=user.email)

    return {
        "message": "account created! Check email to verify your account.",
        "user": results
    }

@auth_router.post("/users/admin/registration", response_model=Union[UserSignUpResponse, UserExist], status_code=status.HTTP_201_CREATED)
async def register_admin_user(admin: AdminSignUp, _: Annotated[User, Depends(RoleChecker(["admin"]))], session: AsyncSession = Depends(get_async_session)):
    results = await user_service.create_user(session=session, user=admin)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="admin registration failed, try again")
    if isinstance(results, UserExist):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results.model_dump())
    
    send_password_reset_email(email=admin.email)

    return {
        "message": "admin account has been created and an email sent to reset their password.",
        "user": results
    }

@auth_router.post("/users/login", response_model=Token, status_code=status.HTTP_200_OK)
async def user_login(login_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    results = await user_service.authenticate_user(session=session, username=login_data.username, password=login_data.password)
    if not results:
        raise InvalidCredentialsException()
    return Token(
        access_token=create_access_token(results.username, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        refresh_token=create_refresh_token(results.username, expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)),
        token_type="bearer"
    )

@auth_router.post("/users/password-reset")
async def password_reset_request(email_data: PasswordResetRequest):
    send_password_reset_email(email=email_data.email)

    return JSONResponse(
        content={
            "message": "please check your email for instructions to reset your password."
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post("/users/password-reset-confirm/{token}")
async def password_reset_request(token: str, password_data: PasswordResetConfirm, session: AsyncSession = Depends(get_async_session)):
    new_password = password_data.new_password
    confirm_password = password_data.confirm_new_paddword
    token_data = decode_url_safe_token(token)

    if new_password != confirm_password:
        raise PasswordsMismatchException()
    user_email = token_data.get("email")
    error_message = token_data.get("error")
    if user_email:
        user = await user_service.get_user_by_email(session=session, email=user_email)
        if not user or not user.is_active:
            raise UserInactiveOrNotFoundException()
        
        hashed_password = get_password_hash(new_password)
        await user_service.update_user(session=session, user=user, update_data={"password": hashed_password})
        
        return JSONResponse(
            content={"message": "password has been reset successfully."},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message": error_message, "error_code": "CE015"},
        status_code=status.HTTP_400_BAD_REQUEST
    )

@auth_router.put("/users/{id}", response_model=UserSignUpResponse, status_code=status.HTTP_200_OK)
async def modify_user(id: str, current_user: Annotated[User, Depends(RoleChecker(["admin", "user"]))], update_data: UserUpdate, session: AsyncSession = Depends(get_async_session)):
    existing_user = await user_service.get_user_by_id(session=session, id=id)
    send_verification_email = False

    if not existing_user:
        raise ResourceNotFoundException()
    
    # check if a new email is being set and if it is unique
    if update_data.email != existing_user.email:
        send_verification_email = True
        email_exists = await user_service.get_user_by_email(session=session, email=update_data.email)
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail={
                    "message": "user with the provided data already exist",
                    "error_code": "CE006"
                }
            )
    results = await user_service.modify_user_logic(
        session=session,
        send_verification_email=send_verification_email,
        existing_user=existing_user,
        current_user=current_user,
        update_data=update_data
    )
    return results

# Add a delete user endpoint
@auth_router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str, current_user: Annotated[User, Depends(RoleChecker(["admin", "user"]))], session: AsyncSession = Depends(get_async_session), token_details=Depends(access_token_bearer)):
    if current_user.role == "user" and str(current_user.id) != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail={
                "message": "please provide the correct user id",
                "error_code": "CE017"
            }
        )
    await user_service.delete_user(session=session, id=id)
    # e3594ed1-ea14-42d2-ba45-a45853a7dc5d
    if current_user.role == "user":
        token_id = token_details.get("token_id")
        token_blocked = await add_token_id_to_blocklist(token_id)
        
        if token_blocked.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail={
                    "message": f"an error occurred while deleting the user: {token_blocked.get("error")}",
                    "error_code": "SE002"
                }
            )
    return
