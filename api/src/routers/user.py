from typing import Annotated
from fastapi import APIRouter, Depends, Query

from database.db import DB, get_db
from schemas.user import UserSchema, UserInfoSchema, ChangePasswordSchema, Referral
from schemas.common import ResultSchema
from dependencies.auth import get_current_active_user, get_current_user
from services.user_service import UserService


router = APIRouter(tags=["User operations"])


@router.get("")
async def get_user_info(
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


@router.get("/referrals", response_model=list[Referral])
async def get_referrals(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
    level: Annotated[int, Query(ge=1, le=5)] = 1,
) -> list[Referral]:
    return await UserService(db).get_referrals(current_user, level=level)
