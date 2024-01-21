from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
)

from config import settings
from repositories.UserRepository import UserRepository
from repositories.MasterReferralRepository import MasterReferralRepository


DATABASE_URL: str = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_TCP_PORT}/{settings.MYSQL_DATABASE}"

engine: AsyncEngine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class DB:
    def __init__(self) -> None:
        self._session_factory = async_session_maker

    async def __aenter__(self):
        self._session = self._session_factory()
        self.users = UserRepository(self._session)
        self.master_referrals = MasterReferralRepository(self._session)
        return self

    async def __aexit__(self, *args) -> None:
        await self.rollback()
        await self._session.close()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def commit(self) -> None:
        await self._session.commit()


async def get_db():
    async with DB() as db:
        yield db
