from datetime import datetime
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from typing import TypedDict

from pydantic import ValidationError
from ipaddress import IPv4Address

from database.db import DB
from schemas.user import (
    UserSchema,
    RegisterUserInSchema,
    TokenSchema,
    MasterReferralSchema,
    UserToSaveSchema,
    ChangePasswordSchema,
)
from schemas.email import EmailSchema
from utils.security import SecurityHasher, JWTAuthController
from utils.validation_errors import AppError
from utils.specific import gen_rand_alphanum_str
from services.redis_service import RedisService


class UserService:
    """User Service represents business logic for users domain"""

    def __init__(self, db: DB):
        self.db = db

    async def update_online_and_ip(
        self, user: UserSchema, request: Request
    ) -> UserSchema:
        user.ip_address = IPv4Address(request.client.host) if request.client else None
        user.last_online = datetime.utcnow()
        updated_user = await self.db.users.update(user.id, user.model_dump())
        return UserSchema.model_validate(updated_user)

    async def get_user_by_name(self, username: str) -> UserSchema | None:
        db_user = await self.db.users.get_by_name(username)
        if db_user is None:
            return None
        return UserSchema.model_validate(db_user)

    async def get_user_by_email(self, email: str) -> UserSchema:
        try:
            validated_email = EmailSchema(email=email).email
        except ValidationError:
            raise AppError.EMAIL_NOT_REGISTERED

        db_user = await self.db.users.get_by_email(validated_email)
        if db_user is None:
            raise AppError.EMAIL_NOT_REGISTERED
        user = UserSchema.model_validate(db_user)
        return user

    async def authenticate_user(self, username: str, password: str) -> TokenSchema:
        user = await self.get_user_by_name(username)
        if user is None:
            raise AppError.INVALID_CREDENTIALS

        if not SecurityHasher.verify_password(password, user.password_hash):
            raise AppError.INVALID_CREDENTIALS
        token = self.create_auth_token(user)
        await RedisService.add_active_session(user.username, token.access_token)
        return token

    @classmethod
    async def logout_user(cls, user: UserSchema) -> None:
        await RedisService.del_active_session(user.username)

    def create_auth_token(self, user: UserSchema) -> TokenSchema:
        token = JWTAuthController.encode(username=user.username)
        return TokenSchema(access_token=token, token_type="bearer")

    async def create_affiliate_code(self) -> str:
        """Create affiliate code. Func checks if code already exists in DB
        Returns:
            str: Return valid unique affiliate code for user
        """
        tries = 10
        while tries > 0:
            code = gen_rand_alphanum_str(10)
            if not await self.db.users.check_existance_by(affiliate_code=code):
                return code
            tries -= 1
        raise AppError.GENERATING_AFFILIATE_CODE_FAILS

    async def register_user(
        self, register_data: RegisterUserInSchema, request: Request
    ) -> UserSchema:
        """Creates user in DB

        Args:
            register_data (UserRegisterIn): Income register pydantic schema

        Raises:
            RegistrationError.EMAIL_EXISTS: Represents error to show that email already exists
            RegistrationError.USERNAME_EXISTS: Represents error to show that username already exists
            RegistrationError.INVALID_AFFILIATE_CODE: Represents error to show that affiliate code failed to be created

        Returns:
            UserRegisterOut: Outcome register pydantic schema
        """
        errors: list[TypedDict] = []
        if await self.db.users.check_existance_by(email=register_data.email):
            errors.append(AppError.EMAIL_EXISTS)
        if await self.db.users.check_existance_by(username=register_data.username):
            errors.append(AppError.USERNAME_EXISTS)

        master = await self.db.users.get_by_affiliate_code(register_data.affiliate_code)
        if master is None:
            errors.append(AppError.INVALID_AFFILIATE_CODE)
        if errors:
            raise RequestValidationError(errors=errors)

        user_ip = request.client.host if request.client else None
        user_data = dict(
            affiliate_code=await self.create_affiliate_code(),
            password_hash=SecurityHasher.get_password_hash(register_data.password),
            ip_address=user_ip,
            **register_data.model_dump(),
        )
        user_to_save = UserToSaveSchema.model_validate(user_data)
        registered_user = UserSchema.model_validate(
            await self.db.users.add(user_to_save.model_dump())
        )
        # Adding master_referral association (current user is a referral for master user)
        master_referral_record = MasterReferralSchema(master_id=master.id, referral_id=registered_user.id)  # type: ignore
        await self.db.master_referrals.add(master_referral_record.model_dump())
        # Adding finance row for current user
        await self.db.finance.add({"user_id": registered_user.id})
        return registered_user

    @staticmethod
    def create_verification_code() -> str:
        return gen_rand_alphanum_str(5)

    async def verify_user(self, user: UserSchema, verification_code: str) -> None:
        if user.is_active:
            return
        saved_verification_code = await RedisService.get_verification_code_for_user(
            user.username
        )
        if verification_code != saved_verification_code:
            raise AppError.INVALID_VERIFICATION_CODE
        user.is_active = True
        await self.db.users.update(user.id, user.model_dump())

    @staticmethod
    async def create_reset_password_token(user: UserSchema) -> str:
        token = SecurityHasher.get_timed_hash(user.username)

        await RedisService.save_reset_password_token(user.email, token)
        return token

    @staticmethod
    async def verify_reset_password_token(email: str, token: str) -> None:
        reset_token = await RedisService.get_reset_password_token(email)
        if token != reset_token:
            raise AppError.INVALID_RESET_TOKEN_OR_EMAIL
        await RedisService.delete_reset_password_token(email)

    async def reset_password(self, email: str, password: str) -> UserSchema:
        db_user = await self.db.users.get_by_email(email)
        if db_user is None:
            raise AppError.EMAIL_NOT_REGISTERED

        user = UserSchema.model_validate(db_user)
        user.password_hash = SecurityHasher.get_password_hash(password)
        user = await self.db.users.update(user.id, user.model_dump())
        return UserSchema.model_validate(user)

    async def change_password(
        self, user: UserSchema, change_password_schema: ChangePasswordSchema
    ) -> UserSchema:
        if not SecurityHasher.verify_password(
            change_password_schema.password,
            user.password_hash,
        ):
            raise AppError.INVALID_PASSWORD

        new_password_hash = SecurityHasher.get_password_hash(
            change_password_schema.new_password
        )
        updated_user = await self.db.users.update(
            user.id, data={"password_hash": new_password_hash}
        )
        await RedisService.del_active_session(user.username)
        return UserSchema.model_validate(updated_user)
