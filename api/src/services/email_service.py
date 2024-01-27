from typing import Any
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pathlib import Path
from schemas.user import UserSchema

from config import settings
from schemas.email import EmailVerificationSchema, EmailResetPasswordSchema
from utils.validation_errors import AppError
from services.redis_service import RedisService


class EmailService:
    _sender = FastMail(
        ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email",
        )
    )

    @classmethod
    async def send_html_email(
        cls,
        subject: str,
        recipients: list[str],
        template_body: dict[str, Any],
        template_name,
    ) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=template_body,
            subtype=MessageType.html,
        )
        await cls._sender.send_message(message, template_name=template_name)

    @classmethod
    async def send_raw_email(cls) -> None:
        raise NotImplementedError

    @classmethod
    async def check_email_allowed_and_emaillock(cls, user: UserSchema):
        if not user.email_allowed:
            raise AppError.EMAIL_NOT_ALLOWED

        if await RedisService.email_lock_exists(user.username):
            raise AppError.EMAIL_LOCK_EXISTS

    @classmethod
    async def send_account_verification_email(
        cls, data: EmailVerificationSchema
    ) -> None:
        await cls.send_html_email(
            subject="MiningVit Account Verification",
            recipients=[data.user.email],
            template_body={
                "username": data.user.username,
                "verification_code": data.verification_code,
            },
            template_name="verification_email.html",
        )
        await RedisService.save_email_lock(data.user.username)

    @classmethod
    async def send_reset_password_email(cls, data: EmailResetPasswordSchema):
        await cls.send_html_email(
            subject="MiningVit Password Recovery ",
            recipients=[data.user.email],
            template_body={
                "username": data.user.username,
                "token": data.token,
            },
            template_name="reset_password_email.html",
        )
        await RedisService.save_email_lock(data.user.username)
