from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from database.db import DB, get_db
from schemas.user import ResetPasswordInSchema, TokenSchema, VerificationCode
from services.user_service import UserService
from services.email_service import EmailService
from services.redis_service import RedisService
from schemas.user import (
    RegisterUserInSchema,
    RegisterUserOutSchema,
    UserSchema,
    ResultSchema,
)
from schemas.email import EmailVerificationSchema, EmailResetPasswordSchema
from dependencies.auth import get_current_user


router = APIRouter(tags=["Authorization/Registration"])


@router.post("/token")
async def login_for_token(
    db: Annotated[DB, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenSchema:
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    return user_service.create_auth_token(user)


@router.post("/register", status_code=201)
async def registration(
    register_data: RegisterUserInSchema,
    background_tasks: BackgroundTasks,
    db: Annotated[DB, Depends(get_db)],
) -> RegisterUserOutSchema:
    user_service = UserService(db)
    user = await user_service.register_user(register_data)
    await db.commit()
    await EmailService.check_email_allowed_and_emaillock(user)
    verification_code = user_service.create_verification_code()
    await RedisService.save_verification_code_for_user(user.username, verification_code)
    background_tasks.add_task(
        EmailService.send_account_verification_email,
        EmailVerificationSchema(
            user=user,
            verification_code=verification_code,
        ),
    )
    return RegisterUserOutSchema(**user.model_dump())


@router.get("/verification")
async def get_verification_code(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
) -> ResultSchema:
    await EmailService.check_email_allowed_and_emaillock(current_user)
    verification_code = UserService.create_verification_code()
    await RedisService.save_verification_code_for_user(
        current_user.username, verification_code
    )

    background_tasks.add_task(
        EmailService.send_account_verification_email,
        EmailVerificationSchema(
            user=current_user,
            verification_code=verification_code,
        ),
    )
    return ResultSchema(result="email was send")


@router.post("/verification")
async def verify_user(
    verification_code: VerificationCode,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[DB, Depends(get_db)],
) -> ResultSchema:
    await UserService(db).verify_user(current_user, verification_code)
    await db.commit()
    return ResultSchema(result="user was activated")


@router.get("/reset_password/{email}")
async def request_reset_password(
    email: str, background_tasks: BackgroundTasks, db: Annotated[DB, Depends(get_db)]
) -> ResultSchema:
    user = await UserService(db).get_user_by_email(email)

    await EmailService.check_email_allowed_and_emaillock(user)
    token = await UserService.create_reset_password_token(user)
    background_tasks.add_task(
        EmailService.send_reset_password_email,
        EmailResetPasswordSchema(
            user=user,
            token=token,
        ),
    )
    return ResultSchema(result="email was send")


@router.post("/reset_password/")
async def reset_password(
    data: ResetPasswordInSchema, db: Annotated[DB, Depends(get_db)]
) -> ResultSchema:
    await UserService.verify_reset_password_token(data.email, data.reset_token)
    await UserService(db).reset_password(data.email, data.password)
    return ResultSchema(result="Password was updated")
