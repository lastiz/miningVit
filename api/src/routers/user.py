from typing import Annotated
from fastapi import APIRouter, Depends

from database.db import DB, get_db
from schemas.user import UserSchema, UserInfoSchema, ChangePasswordSchema
from schemas.common import ResultSchema
from dependencies.auth import get_current_active_user, get_current_user
from services.user_service import UserService


router = APIRouter(tags=["Authorization/Registration"])


@router.get("")
async def get_user(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
) -> UserInfoSchema:
    return UserInfoSchema.model_validate(current_user)


@router.post("/change_password")
async def change_password(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
    change_password_schema: ChangePasswordSchema,
) -> ResultSchema:
    try:
        await UserService(db).change_password(current_user, change_password_schema)
        await db.commit()
    except BaseException as err:
        raise err

    return ResultSchema(result="password was changed")
