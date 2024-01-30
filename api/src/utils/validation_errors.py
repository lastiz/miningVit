from fastapi import status, HTTPException
from typing import TypedDict


class ValidationErrorDetails(TypedDict):
    loc: list[str]
    msg: str
    code: int


class HTTPErrorDetails(TypedDict):
    location: str
    message: str
    code: int


class AppError:
    INVALID_CREDENTIALS = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
        detail=HTTPErrorDetails(
            location="credentials",
            message="Could not validate credentials",
            code=998,
        ),
    )
    INACTIVE_USER = HTTPException(
        status_code=418,
        detail=HTTPErrorDetails(
            location="user",
            message="Inactive user",
            code=999,
        ),
    )
    EMAIL_EXISTS = ValidationErrorDetails(
        loc=["email"],
        msg="Email already exists",
        code=1000,
    )
    USERNAME_EXISTS = ValidationErrorDetails(
        loc=["username"],
        msg="Username already exists",
        code=1001,
    )
    INVALID_AFFILIATE_CODE = ValidationErrorDetails(
        loc=["affiliate_code"],
        msg="Invalid affiliate code",
        code=1002,
    )
    GENERATING_AFFILIATE_CODE_FAILS = HTTPException(
        status_code=500,
        detail=HTTPErrorDetails(
            location="server",
            message="Generating affiliate code failse, try later",
            code=1003,
        ),
    )
    EMAIL_NOT_ALLOWED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="email_allowed",
            message="Email not allowed for user",
            code=1004,
        ),
    )
    EMAIL_LOCK_EXISTS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="email_lock",
            message="Email lock exists. Try after 3 minutes",
            code=1005,
        ),
    )
    EMAIL_NOT_REGISTERED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="email",
            message="Email not registered",
            code=1006,
        ),
    )
    INVALID_RESET_TOKEN_OR_EMAIL = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="email, reset_token",
            message="Invalid reset token or email",
            code=1007,
        ),
    )
    INVALID_VERIFICATION_CODE = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="code",
            message="Invalid verification code",
            code=1008,
        ),
    )
    FAILED_TO_UPDATE_USER = HTTPException(
        status_code=500,
        detail=HTTPErrorDetails(
            location="server",
            message="Failed to update user",
            code=1009,
        ),
    )
    INVALID_PASSWORD = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="password",
            message="invalid current password",
            code=1010,
        ),
    )
