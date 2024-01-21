from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from services.user_service import UserService
import schemas.user as user_schema
from utils.security import JWTAuthController
from utils.validation_errors import AppError
from database.db import DB, get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    db: Annotated[DB, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> user_schema.UserSchema:
    try:
        payload = JWTAuthController.decode(token)
        username: str | None = payload.get("username")
        if username is None:
            raise AppError.INVALID_CREDENTIALS
    except PyJWTError:
        raise AppError.INVALID_CREDENTIALS
    user = await UserService(db).get_user_by_name(username=username)
    if user is None:
        raise AppError.INVALID_CREDENTIALS
    return user


async def get_current_active_user(
    current_user: Annotated[user_schema.UserSchema, Depends(get_current_user)]
) -> user_schema.UserSchema:
    if not current_user.is_active:
        raise AppError.INACTIVE_USER
    return current_user
