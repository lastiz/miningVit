from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from src.database.db import engine
from fastapi.testclient import TestClient
from src.main import app

from src.database.models import Base
from src.config import settings


engine_test = create_async_engine(settings.DB_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    bind=engine_test,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    async def mock_send_account_verification_email(*args, **kwargs):
        return True

    async def mock_send_reset_password_email(*args, **kwargs):
        return True

    monkeypatch.setattr(
        "services.email_service.EmailService.send_account_verification_email",
        mock_send_account_verification_email,
    )
    monkeypatch.setattr(
        "services.email_service.EmailService.send_reset_password_email",
        mock_send_reset_password_email,
    )


@pytest.fixture(autouse=True)
def mock_redis_service(monkeypatch):
    async def mock_save_email_lock(*args, **kwargs):
        return True

    async def mock_email_lock_exists(*args, **kwargs):
        return False

    monkeypatch.setattr(
        "services.redis_service.RedisService.save_email_lock",
        mock_save_email_lock,
    )
    monkeypatch.setattr(
        "services.redis_service.RedisService.email_lock_exists",
        mock_email_lock_exists,
    )


@pytest.fixture(autouse=True)
def mock_user_service(monkeypatch):
    def mock_create_verification_code(*args, **kwargs):
        return "11111"

    monkeypatch.setattr(
        "services.user_service.UserService.create_verification_code",
        mock_create_verification_code,
    )


@pytest.fixture(scope="session")
async def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True, scope="session")
async def setup_db():
    """Create all tables in db and then delete all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
