from sqlalchemy.ext.asyncio import AsyncSession

from .base import GenericSqlRepository
from database.models import Machine
from repositories.purchased_machine_repository import PurchasedMachineRepository


class MachineRepository(GenericSqlRepository[Machine]):
    def __init__(self, session: AsyncSession) -> None:
        self.purchased = PurchasedMachineRepository(session)
        super().__init__(session, Machine)
