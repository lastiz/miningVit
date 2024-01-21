from pydantic import EmailStr, BaseModel

from schemas.user import VerificationCode, UserSchema


class EmailSchema(BaseModel):
    email: EmailStr


class EmailsSchema(BaseModel):
    emails: list[EmailStr]


class EmailVerificationSchema(BaseModel):
    user: UserSchema
    verification_code: VerificationCode


class EmailResetPasswordSchema(BaseModel):
    user: UserSchema
    token: str
