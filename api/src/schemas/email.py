from pydantic import EmailStr

from .base import Base
from schemas.user import UserSchema


class EmailSchema(Base):
    email: EmailStr


class EmailsSchema(Base):
    emails: list[EmailStr]


class EmailVerificationSchema(Base):
    user: UserSchema
    verification_code: str


class EmailResetPasswordSchema(Base):
    user: UserSchema
    token: str
