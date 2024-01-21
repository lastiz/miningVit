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

    # SECRET KEY AND ALGORITHM
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30

    # APP SPECIFIC


settings = Settings()
