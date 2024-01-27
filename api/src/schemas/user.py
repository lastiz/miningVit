from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Annotated


_USERNAME_PATTERN = r"^[a-zA-Z]{1}[a-zA-Z0-9]{3,14}$"


class Base(BaseModel):
    """Base Pydantic Model"""

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class RegisterUserInSchema(Base):
    """Pydantic Model represents client data for register account"""

    username: Annotated[str, Field(pattern=_USERNAME_PATTERN)]
    email: EmailStr
    password: Annotated[str, Field(min_length=6, max_length=16)]
    affiliate_code: Annotated[str, Field(exclude=True)]


class RegisterUserOutSchema(Base):
    """Pydantic Model represents data to show user after registration"""

    username: str
    email: EmailStr
    affiliate_code: str


class UserSchema(Base):
    """Pydantic Model represents user record in DB"""

    id: int
    username: str
    email: str
    email_allowed: bool
    telegram: str | None
    password_hash: str
    is_admin: bool
    is_active: bool
    affiliate_code: str
    note: str | None


class UserToSaveSchema(Base):
    """Pydantic Model represents user record to save in DB"""

    username: str
    email: str
    telegram: str | None = None
    password_hash: str
    is_admin: bool = False
    is_active: bool = False
    affiliate_code: str
    note: str | None = None


class TokenSchema(Base):
    """Pydantic Model represents token to send user after login"""

    access_token: str
    token_type: str


class PasswordSchema(Base):
    password: Annotated[str, Field(min_length=6, max_length=16)]


class ResetPasswordInSchema(PasswordSchema):
    email: EmailStr
    reset_token: str


class MasterReferralSchema(Base):
    """Pydantic Model represents master_referral record in DB"""

    master_id: int
    referral_id: int


class ResultSchema(Base):
    result: str


class VerificationCode(Base):
    code: str
