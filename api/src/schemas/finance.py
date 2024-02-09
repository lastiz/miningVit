from .base import Base
from utils.enums import TransactionStatus, IncomeType


class FinanceInfoSchema(Base):
    id: int
    wallet: str | None
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
    status: TransactionStatus
    type: IncomeType
    amount: int


class DepositsSchema(Base):
    deposits: list[DepositSchema]


class WithdrawalsSchema(Base):
    withdrawals: list[WithdrawalSchema]


class IncomesSchema(Base):
    incomes: list[IncomeSchema]


class WithdrawInSchema(Base):
    amount: int
