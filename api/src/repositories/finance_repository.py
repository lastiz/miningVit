from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import raiseload

from .base import GenericSqlRepository
from database.models import Finance, Deposit, Withdrawal, Income
from utils.validation_errors import AppError


class FinanceRepository(GenericSqlRepository[Finance]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Finance)

    async def get_user_finance(self, user_id: int) -> Finance | None:
        stmt = select(Finance).filter_by(user_id=user_id).options(raiseload("*"))
        return await self._session.scalar(stmt)

    async def get_user_deposits(self, user_id: int) -> list[Deposit]:
        stmt = select(Finance.deposits).filter_by(user_id=user_id)

        deposits = await self._session.scalar(stmt)
        if deposits is None:
            return []
        return deposits

    async def get_user_withdrawals(self, user_id: int) -> list[Withdrawal]:
        stmt = select(Finance.withdrawals).filter_by(user_id=user_id)
        withdrawals = await self._session.scalar(stmt)
        if withdrawals is None:
            return []
        return withdrawals

    async def get_user_incomes(self, user_id: int) -> list[Income]:
        stmt = select(Finance.incomes).filter_by(user_id=user_id)
        incomes = await self._session.scalar(stmt)
        if incomes is None:
            return []
        return incomes

    async def add_user_deposit(self, user_id: int, data: dict[str, Any]):
        user_finance = await self.get_user_finance(user_id)
        if user_finance is None:
            raise AppError.COULD_NOT_GET_FINANCE

        user_finance.deposits.append(Deposit(**data))
        await self._session.flush()

    async def add_user_income(self, user_id: int, data: dict[str, Any]):
        user_finance = await self.get_user_finance(user_id)
        if user_finance is None:
            raise AppError.COULD_NOT_GET_FINANCE

        user_finance.incomes.append(Income(**data))
        await self._session.flush()

    async def add_user_withdrawal(self, user_id: int, data: dict[str, Any]):
        user_finance = await self.get_user_finance(user_id)
        if user_finance is None:
            raise AppError.COULD_NOT_GET_FINANCE

        user_finance.withdrawals.append(Withdrawal(**data))
        await self._session.flush()
