from typing import Any
from datetime import timedelta

from repositories.redis_repository import redis_repo
from config import settings


class RedisService:
    _VERIFICATION_KEY_EXPIRE_AFTER: int = int(
        timedelta(hours=settings.VERIFY_KEY_EXPIRE_HOURS).total_seconds()
    )
    _EMAIL_LOCK_EXPIRE_MINUTES: int = int(
        timedelta(minutes=settings.EMAIL_LOCK_EXPIRE_MINUTES).total_seconds()
    )
    _RESET_PASSWORD_TOKEN_EXPIRE_HOURS: int = int(
        timedelta(hours=settings.RESET_PASSWORD_TOKEN_EXPIRE_HOURS).total_seconds()
    )
    _AUTH_SESSION_TIME: int = int(
        timedelta(settings.ACCESS_TOKEN_EXPIRE_DAYS).total_seconds()
    )
    _WITHDRAWAL_LOCK_EXPIRE_HOURS: int = int(
        timedelta(hours=settings.WITHDRAWAL_LOCK_EXPIRE_HOURS).total_seconds()
    )
    _repository = redis_repo

    @classmethod
    async def init(cls) -> None:
        await cls._repository.init()

    @classmethod
    async def close(cls) -> None:
        await cls._repository.close()

    @classmethod
    async def _get(cls, key: Any) -> Any | None:
        return await cls._repository.get(key)

    @classmethod
    async def _set(cls, key: Any, value: Any, expire: int | None) -> bool:
        return await cls._repository.set(key, value, expire)

    @classmethod
    async def _delete(cls, key: Any) -> bool:
        return await cls._repository.delete(key)

    @classmethod
    async def save_verification_code_for_user(cls, username: str, code: str) -> bool:
        key = f"verify_key:{username}"
        return await cls._set(
            key=key,
            value=code,
            expire=cls._VERIFICATION_KEY_EXPIRE_AFTER,
        )

    @classmethod
    async def save_email_lock(cls, username: str) -> bool:
        key = f"email_lock:{username}"
        return await cls._set(key, 1, expire=cls._EMAIL_LOCK_EXPIRE_MINUTES)

    @classmethod
    async def email_lock_exists(cls, username: str) -> bool:
        key = f"email_lock:{username}"
        value = await cls._get(key)
        if value is None:
            return False
        return True

    @classmethod
    async def get_verification_code_for_user(cls, username: str) -> str | None:
        key = f"verify_key:{username}"
        return await cls._get(key=key)

    @classmethod
    async def save_reset_password_token(cls, email: str, token: str) -> bool:
        key = f"reset_password_token:{email}"
        return await cls._set(key, token, expire=cls._RESET_PASSWORD_TOKEN_EXPIRE_HOURS)

    @classmethod
    async def get_reset_password_token(cls, email: str) -> str | None:
        key = f"reset_password_token:{email}"
        return await cls._get(key)

    @classmethod
    async def delete_reset_password_token(cls, email: str) -> bool:
        key = f"reset_password_token:{email}"
        return await cls._delete(key)

    @classmethod
    async def add_active_session(cls, username: str, token: str) -> int | Any:
        key = f"active_session:{username}"
        return await cls._set(key, token, expire=cls._AUTH_SESSION_TIME)

    @classmethod
    async def get_active_session(cls, username: str) -> str | None:
        key = f"active_session:{username}"
        return await cls._get(key)

    @classmethod
    async def del_active_session(cls, username: str) -> int | Any:
        key = f"active_session:{username}"
        return await cls._repository.delete(key)

    @classmethod
    async def save_withdrawal_lock(cls, username: str) -> bool:
        key = f"withdrawal_lock:{username}"
        return await cls._set(key, value=1, expire=cls._WITHDRAWAL_LOCK_EXPIRE_HOURS)

    @classmethod
    async def get_withdrawal_lock(cls, username: str) -> int | None:
        key = f"withdrawal_lock:{username}"
        return await cls._get(key)
