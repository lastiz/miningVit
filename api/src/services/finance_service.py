from schemas.user import UserSchema
from database.db import DB

from schemas.finance import (
    DepositsSchema,
    FinanceInfoSchema,
    WithdrawalsSchema,
    IncomesSchema,
)
from schemas.machine import MachineSchema
from utils.validation_errors import AppError


class FinanceService:
    """Balance Service represents business logic for balance domain"""

    def __init__(self, db: DB):
        self.db = db

    async def get_user_finance_info(self, user: UserSchema) -> FinanceInfoSchema:
        db_finance = await self.db.finance.get_user_finance(user.id)
        if db_finance is None:
            raise AppError.COULD_NOT_GET_FINANCE
        return FinanceInfoSchema.model_validate(db_finance)

    async def get_user_deposits(self, user: UserSchema):
        db_deposits = await self.db.finance.get_user_deposits(user.id)
        return DepositsSchema.model_validate({"deposits": db_deposits})

    async def get_user_withdrawals(self, user: UserSchema):
        db_withdrawals = await self.db.finance.get_user_withdrawals(user.id)
        return WithdrawalsSchema.model_validate({"withdrawals": db_withdrawals})

    async def get_user_incomes(self, user: UserSchema):
        db_incomes = await self.db.finance.get_user_incomes(user.id)
        return IncomesSchema.model_validate({"incomes": db_incomes})
