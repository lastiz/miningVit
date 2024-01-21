from passlib.context import CryptContext
from config import settings
import jwt
from datetime import datetime, timedelta, timezone
import hashlib


class SecurityHasher:
    _pwd_context = CryptContext(schemes=["bcrypt"])

    @staticmethod
    def get_timed_hash(value) -> str:
        str_to_hash = f"{value}{datetime.utcnow()}"
        return hashlib.sha256(str_to_hash.encode()).hexdigest()

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls._pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls._pwd_context.hash(password)


class JWTAuthController:
    _secret: str = settings.SECRET_KEY
    _algorithm: str = settings.ALGORITHM

    @classmethod
    def encode(cls, **kwargs) -> str:
        expire_at = datetime.now(tz=timezone.utc) + timedelta(
            days=settings.ACCESS_TOKEN_EXPIRE_DAYS
        )
        kwargs.update(dict(exp=expire_at))  # type: ignore
        return jwt.encode(kwargs, cls._secret, algorithm=cls._algorithm)

    @classmethod
    def decode(cls, token: str) -> dict:
        return jwt.decode(token, cls._secret, algorithms=[cls._algorithm])
