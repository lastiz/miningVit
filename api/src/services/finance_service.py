from schemas.user import UserSchema
from database.db import DB

from schemas.finance import (
    DepositsSchema,
    FinanceInfoSchema,
    WithdrawalsSchema,
    IncomesSchema,
)
from utils.validation_errors import AppError
from utils.enums import TransactionStatus
from services.redis_service import RedisService


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

    async def withdraw_funds(self, user: UserSchema, amount: int) -> None:
        """Represents withdraw logic. Creates withdrawal record in database

        Args:
            user (UserSchema): represents user
            amount (int): represents amount to withdraw

        Raises:
            AppError.LOW_BALANCE: raises if user balance is too low
            AppError.NO_WALLET: raises if user has unfilled wallet address
            AppError.WITHDRAWAL_LOCK_EXISTS: raises if withdrawal lock exists in redis db
        """
        user_finance = await self.get_user_finance_info(user)
        if user_finance.balance < amount:
            raise AppError.LOW_BALANCE

        if user_finance.wallet is None:
            raise AppError.NO_WALLET

        withdrawal_lock = await RedisService.get_withdrawal_lock(user.username)
        if withdrawal_lock:
            raise AppError.WITHDRAWAL_LOCK_EXISTS

        await self.db.finance.add_user_withdrawal(
            user_id=user.id,
            data={
                "amount": amount,
                "wallet": user_finance.wallet,
                "status": TransactionStatus.PENDING,
            },
        )
        await RedisService.save_withdrawal_lock(user.username)
