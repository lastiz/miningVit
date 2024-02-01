from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import raiseload, selectinload

from .base import GenericSqlRepository
from database.models import Finance, Deposit, Withdrawal, Income
from utils.validation_errors import AppError


class FinanceRepository(GenericSqlRepository[Finance]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Finance)

    async def get_user_finance(self, user_id: int) -> Finance | None:
        stmt = select(Finance).filter_by(user_id=user_id).options(raiseload("*"))
        return await self._session.scalar(stmt)

    async def get_user_finance_with(
        self, user_id: int, with_: str = "all"
    ) -> Finance | None:
        stmt = select(Finance).filter_by(user_id=user_id)
        if with_ == "all":
            stmt = stmt.options(
                selectinload(Finance.deposits, Finance.withdrawals, Finance.incomes)
            )
        else:
            stmt = stmt.options(selectinload(getattr(Finance, with_)))
        return await self._session.scalar(stmt)

    async def get_user_deposits(self, user_id: int) -> list[Deposit]:
        stmt = select(Deposit).join(Finance).filter(Finance.user_id == user_id)
        deposits = list(await self._session.scalars(stmt))
        return deposits

    async def get_user_withdrawals(self, user_id: int) -> list[Withdrawal]:
        stmt = select(Withdrawal).join(Finance).filter(Finance.user_id == user_id)
        withdrawals = list(await self._session.scalars(stmt))
        return withdrawals

    async def get_user_incomes(self, user_id: int) -> list[Income]:
        stmt = select(Income).join(Finance).filter(Finance.user_id == user_id)
        incomes = list(await self._session.scalars(stmt))
        return incomes

    async def add_user_deposit(self, user_id: int, data: dict[str, Any]):
        user_finance = await self.get_user_finance_with(user_id, with_="deposits")
        if user_finance is None:
            raise AppError.COULD_NOT_GET_FINANCE

        user_finance.deposits.append(Deposit(**data))
        await self._session.flush()

    async def add_user_income(self, user_id: int, data: dict[str, Any]):
        user_finance = await self.get_user_finance_with(user_id, with_="incomes")
        if user_finance is None:
            raise AppError.COULD_NOT_GET_FINANCE

        user_finance.incomes.append(Income(**data))
        await self._session.flush()

    async def add_user_withdrawal(self, user_id: int, data: dict[str, Any]):
        user_finance = await self.get_user_finance_with(user_id, with_="withdrawals")
        if user_finance is None:
            raise AppError.COULD_NOT_GET_FINANCE

        user_finance.withdrawals.append(Withdrawal(**data))
        await self._session.flush()
