from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from .base import GenericSqlRepository
from database.models import User, MasterReferral


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

    async def get_master(self, user: User) -> User | None:
        """Returns User model that represents master of :user

        Args:
            user (User): User db model

        Returns:
            User | None: Returns User model or None
        """
        stmt = (
            select(User)
            .join(MasterReferral, onclause=MasterReferral.master_id == User.id)
            .where(MasterReferral.referral_id == user.id)
        )
        return await self._session.scalar(stmt)

    async def get_referrals(
        self, user: User, level: int = 1, **filters
    ) -> Sequence[User]:
        """Returns list of users(referrals) of :user and
           filtered with :**filters and
           ordered by User.created column in deescending mode
        Args:
            user (User): User (master of referrals) obj
            level (int, optional): Depth level of referrals  Defaults to 1.
            filters (optional kwargs): Additional filters for referrals
        Returns:
            Sequence[User]: Sequence of User objects (referrals of :user)
        """
        if level == 0:
            return []
        # form subquery for referral ids depending on :level
        subq = (user.id,)
        for _ in range(level):
            subq = select(MasterReferral.referral_id).where(
                MasterReferral.master_id.in_(subq)
            )
        # selecting referrals with ids in subq statement
        stmt = (
            select(User)
            .where(User.id.in_(subq))
            .filter_by(**filters)
            .order_by(desc(User.created_at))
        )
        return list((await self._session.scalars(stmt)).unique())
