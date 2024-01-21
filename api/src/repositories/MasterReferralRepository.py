from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import GenericSqlRepository
from database.models import MasterReferral


class MasterReferralRepository(GenericSqlRepository[MasterReferral]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MasterReferral)
