from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import GenericSqlRepository
from database.models import User


class UserRepository(GenericSqlRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_name(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return await self._session.scalar(stmt)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return await self._session.scalar(stmt)

    async def get_by_affiliate_code(self, affiliate_code: str) -> User | None:
        stmt = select(User).where(User.affiliate_code == affiliate_code)
        return await self._session.scalar(stmt)

    async def check_existance_by(self, **kwargs) -> bool:
        exists = await self.list(**kwargs)
        return True if exists else False
