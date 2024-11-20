from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError


class ToDOApiException(Exception):
    """This is the base class for all ToDo Api errors"""
    pass


class InvalidTokenException(ToDOApiException):
    """An invalid or expired token was provided"""
    pass


class RevokedTokenException(ToDOApiException):
    """A revoked token was provided"""
    pass


class AccessTokenRequiredException(ToDOApiException):
    """An access token is required"""
    pass


class RefreshTokenRequiredException(ToDOApiException):
    """A refresh token is required"""
    pass


class UserAlreadyExistsException(ToDOApiException):
    """The provided email or username at sign up is already existing"""
    pass


class InvalidCredentialsException(ToDOApiException):
    """Wrong credentials(username/password) were provided during signing in"""
    pass


class InsufficientPermissionException(ToDOApiException):
    """A user has inadequate permissions to perform an action."""
    pass


class UnverifiedUserException(ToDOApiException):
    """The user is not verified."""
    pass


class InactiveUSerException(ToDOApiException):
    """The user is inactive."""
    pass


class InvalidTokenDataException(ToDOApiException):
    """The token data could not be validated."""
    pass


class InvalidVerifyTokenDataException(ToDOApiException):
    """The verify user account token data could not be validated."""
    pass


class ResourceNotFoundException(ToDOApiException):
    """The requested resource is not found."""
    pass

class PasswordsMismatchException(ToDOApiException):
    """The provided passwords do not match."""
    pass


class UserInactiveOrNotFoundException(ToDOApiException):
    """User is either not found or is inactive."""
    pass


class InternalServerErrorException(ToDOApiException):
    """Custom HTTP 500 error"""
    pass


def create_exception_handler(status_code: int, details: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(r: Request, e: ToDOApiException):
        return JSONResponse(
            content=details,
            status_code=status_code
        ) 
    return exception_handler

def register_custom_errors(app: FastAPI):
    app.add_exception_handler(
        InvalidTokenException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={
                "message": "invalid or expired token, please get a new token",
                "error_code": "CE001"
            }
        )
    )
    app.add_exception_handler(
        RevokedTokenException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={
                "message": "invalid or revoked token, please get a new token",
                "error_code": "CE002"
            }
        )
    )
    app.add_exception_handler(
        AccessTokenRequiredException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={
                "message": "please provide an access token",
                "error_code": "CE003"
            }
        )
    )
    app.add_exception_handler(
        RefreshTokenRequiredException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={
                "message": "please provide a refresh token",
                "error_code": "CE004"
            }
        )
    )
    app.add_exception_handler(
        InvalidCredentialsException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "message": "incorrect username or password",
                "error_code": "CE005"
            }
        )
    )
    app.add_exception_handler(
        UserAlreadyExistsException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "message": "a user with the provided data already exist",
                "error_code": "CE006"
            }
        )
    )
    app.add_exception_handler(
        InsufficientPermissionException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            details={
                "message": "not enough permissions for this operation",
                "error_code": "CE007"
            }
        )
    )
    app.add_exception_handler(
        UnverifiedUserException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            details={
                "message": "user not verified",
                "error_code": "CE008"
            }
        )
    )
    app.add_exception_handler(
        InactiveUSerException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            details={
                "message": "user is inactive",
                "error_code": "CE009"
            }
        )
    )
    app.add_exception_handler(
        InvalidTokenDataException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={
                "message": "could not validate token data",
                "error_code": "CE010"
            }
        )
    )
    app.add_exception_handler(
        InvalidVerifyTokenDataException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "message": "invalid user verification token",
                "error_code": "CE011"
            }
        )
    )
    app.add_exception_handler(
        ResourceNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            details={
                "message": "resource not found",
                "error_code": "CE012"
            }
        )
    )
    app.add_exception_handler(
        PasswordsMismatchException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "message": "passwords do not match",
                "error_code": "CE013"
            }
        )
    )
    app.add_exception_handler(
        UserInactiveOrNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "message": "user not found or is inactive. If this is a mistake, please contact us for support",
                "error_code": "CE014"
            }
        )
    )
    app.add_exception_handler(
        InternalServerErrorException,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={
                "message": "something went wrong while processing the request",
                "error_code": "SE001"
            }
        )
    )
