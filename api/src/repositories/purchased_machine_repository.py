from sqlalchemy.ext.asyncio import AsyncSession

from .base import GenericSqlRepository
from database.models import PurchasedMachine


class PurchasedMachineRepository(GenericSqlRepository[PurchasedMachine]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PurchasedMachine)
