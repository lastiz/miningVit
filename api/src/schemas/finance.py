from pydantic import BaseModel, ConfigDict

from utils.enums import TransactionStatus, IncomeType


class Base(BaseModel):
    """Base Pydantic Model"""

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        validate_assignment=True,
    )


class FinanceInfoSchema(Base):
    balance: int
    income: int
    affiliate_income: int


class DepositSchema(Base):
    status: TransactionStatus
    amount: int
    platform: str


class WithdrawalSchema(Base):
    status: TransactionStatus
    amount: int
    wallet: str


class IncomeSchema(Base):
    type: IncomeType
    amount: int


class DepositsSchema(Base):
    deposits: list[DepositSchema]


class WithdrawalsSchema(Base):
    withdrawals: list[WithdrawalSchema]


class IncomesSchema(Base):
    incomes: list[IncomeSchema]
