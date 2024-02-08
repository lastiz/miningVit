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
            message="could not validate credentials",
            code=998,
        ),
    )
    INACTIVE_USER = HTTPException(
        status_code=418,
        detail=HTTPErrorDetails(
            location="user",
            message="inactive user",
            code=999,
        ),
    )
    EMAIL_EXISTS = ValidationErrorDetails(
        loc=["email"],
        msg="email already exists",
        code=1000,
    )
    USERNAME_EXISTS = ValidationErrorDetails(
        loc=["username"],
        msg="username already exists",
        code=1001,
    )
    INVALID_AFFILIATE_CODE = ValidationErrorDetails(
        loc=["affiliate_code"],
        msg="invalid affiliate code",
        code=1002,
    )
    GENERATING_AFFILIATE_CODE_FAILS = HTTPException(
        status_code=500,
        detail=HTTPErrorDetails(
            location="server",
            message="generating affiliate code failse, try later",
            code=1003,
        ),
    )
    EMAIL_NOT_ALLOWED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="email_allowed",
            message="email not allowed for user",
            code=1004,
        ),
    )
    EMAIL_LOCK_EXISTS = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="email_lock",
            message="email lock exists. Try after 3 minutes",
            code=1005,
        ),
    )
    EMAIL_NOT_REGISTERED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="email",
            message="email not registered",
            code=1006,
        ),
    )
    INVALID_RESET_TOKEN_OR_EMAIL = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="email, reset_token",
            message="invalid reset token or email",
            code=1007,
        ),
    )
    INVALID_VERIFICATION_CODE = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="code",
            message="invalid verification code",
            code=1008,
        ),
    )
    FAILED_TO_UPDATE_USER = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=HTTPErrorDetails(
            location="server",
            message="failed to update user",
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

    # FINANCE ERRORS
    COULD_NOT_GET_FINANCE = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=HTTPErrorDetails(
            location="server",
            message="failed to load user finance",
            code=1011,
        ),
    )
    INSUFFICIENT_BALANCE = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="balance",
            message="insufficient user balance",
            code=1012,
        ),
    )

    # MACHINE ERRORS
    MACHINE_NOT_OWNED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="purchased_machine_id",
            message="user does not own this machine",
            code=1013,
        ),
    )
    MACHINE_NOT_FOUND = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="purchased_machine_id",
            message="machine not found",
            code=1014,
        ),
    )
    INVALID_REQUEST_TIME = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="purchased machine.activated_time",
            message="invalid request time",
            code=1015,
        ),
    )
    MACHINE_NOT_ACTIVATED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="purchased machine.activated_time",
            message="machine not activated",
            code=1016,
        ),
    )
    MACHINE_ALREADY_PURCHASED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=HTTPErrorDetails(
            location="machine_coin",
            message="machine already purchased",
            code=1017,
        ),
    )
