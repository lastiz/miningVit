from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env", extra="ignore"
    )

    # EMAIL SERVICE
    MAIL_SERVER: str = "mail.example.com"
    MAIL_PORT: int = 465
    MAIL_USERNAME: str = "me@example.com"
    MAIL_FROM: str = "me@example.com"
    MAIL_FROM_NAME: str = "example name"
    MAIL_PASSWORD: str = "example password"
    MAIL_SSL_TLS: bool = True
    MAIL_STARTTLS: bool = False

    # MYSQL
    MYSQL_HOST: str = "localhost"
    MYSQL_TCP_PORT: str = "3306"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "example"

    # REDIS
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    VERIFY_KEY_EXPIRE_HOURS: int = 24
    EMAIL_LOCK_EXPIRE_MINUTES: int = 3
    RESET_PASSWORD_TOKEN_EXPIRE_HOURS: int = 1
    WITHDRAWAL_LOCK_EXPIRE_HOURS: int = 24

    # SECRET KEY AND ALGORITHM
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30

    # APP SPECIFIC
    ADMIN_NAME: str = "admin"
    ADMIN_EMAIL: str = "admin@admin.com"
    ADMIN_PASSWORD: str = "admin"
    ADMIN_AFFILIATE_CODE: str = "0000000000"
    COMMISSION_HOURS_DELTA: int = 24
    MACHINES_INFO: list[dict[str, str | int]] = [
        {
            "title": "Bitmain Antminer L7",
            "coin": "LTC",
            "income": 25000,
            "price": 400000,
        },
        {
            "title": "Bitmain Antminer E9 Pro",
            "coin": "ETC",
            "income": 15000,
            "price": 300000,
        },
        {
            "title": "Bitmain Antminer E9",
            "coin": "PIRL",
            "income": 10000,
            "price": 200000,
        },
        {
            "title": "Bitmain Antminer S19k Pro",
            "coin": "BTC",
            "income": 4000,
            "price": 100000,
        },
        {
            "title": "Bitmain Antminer Z15 Pro",
            "coin": "ZEN",
            "income": 2000,
            "price": 50000,
        },
        {
            "title": "Bitmain Antminer Z15",
            "coin": "ZEC",
            "income": 1200,
            "price": 30000,
        },
        {
            "title": "MicroBT Whatsminer M50",
            "coin": "BTCD",
            "income": 400,
            "price": 10000,
        },
        {
            "title": "Bitmain Antminer S19j Pro",
            "coin": "PPC",
            "income": 120,
            "price": 3600,
        },
        {
            "title": "MicroBT Whatsminer M30S",
            "coin": "BCX",
            "income": 40,
            "price": 1200,
        },
    ]
    REFERRAL_SYSTEM: tuple = (0.15, 0, 1, 0.05, 0.03, 0.01)

    @property
    def DB_URL(self) -> str:
        return f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_TCP_PORT}/{settings.MYSQL_DATABASE}"


settings = Settings()
