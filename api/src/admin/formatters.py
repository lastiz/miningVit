from typing import Sequence
from sqladmin.formatters import BASE_FORMATTERS
from datetime import datetime
from sqlalchemy.orm.collections import InstrumentedList

from database.models import (
    PurchasedMachine,
    User,
    MasterReferral,
    Finance,
    Deposit,
    Income,
    Withdrawal,
    Machine,
)


class NotImplementedFormatterError(Exception):
    ...


def to_dollars(val: int) -> float:
    return val / 100


def instrumented_list_formatter(values: InstrumentedList) -> list[str]:
    result = []
    for value in values:
        try:
            value_formatter = FORMATTERS[type(value)]
        except KeyError:
            raise NotImplementedFormatterError(
                f"FORMATTERS don't have formatter for this type {type(value)}"
            )
        result.append(value_formatter(value))
    return result


def datetime_formatter(value: datetime) -> str:
    return value.strftime("%d-%m-%Y")


def user_formater(user: User) -> str:
    return f"(id={user.id} | {user.username} | {user.email})"


def finance_formatter(finance: Finance) -> str:
    return (
        f"(id={finance.id} | "
        f"Balance={to_dollars(finance.balance)}$ | "
        f"Income={to_dollars(finance.income)}$ | "
        f"Affiliate Income={to_dollars(finance.affiliate_income)}$ | "
        f"Wallet={finance.wallet})"
    )


def machine_formatter(machine: Machine) -> str:
    return f"(Coin={machine.coin} | price={to_dollars(machine.price)}$ | income={to_dollars(machine.income)}$)"


def purchased_machine_formatter(purchased_machine: PurchasedMachine) -> str:
    return (
        f"Owner_id={purchased_machine.user_id} | "
        f"Machine_id={purchased_machine.machine_id} | "
        f"Activated_time={datetime_formatter(purchased_machine.activated_time) if purchased_machine.activated_time else None}"
    )


def withdrawal_formatter(withdrawal: Withdrawal) -> str:
    return (
        f"(Status={withdrawal.status} | "
        f"Amount={to_dollars(withdrawal.amount)}$ | "
        f"Created at={datetime_formatter(withdrawal.created_at)})"
    )


def deposit_formatter(deposit: Deposit) -> str:
    return (
        f"(Status={deposit.status} | "
        f"Amount={to_dollars(deposit.amount)}$ | "
        f"Type={deposit.platform} | "
        f"Created at={datetime_formatter(deposit.created_at)})"
    )


def income_formatter(income: Income) -> str:
    return (
        f"(Status={income.status} | "
        f"Amount={to_dollars(income.amount)}$ | "
        f"Type={income.type} | "
        f"Created at={datetime_formatter(income.created_at)})"
    )


FORMATTERS = BASE_FORMATTERS
FORMATTERS.update(
    {
        InstrumentedList: instrumented_list_formatter,
        datetime: datetime_formatter,  # type: ignore
        User: user_formater,
        Finance: finance_formatter,
        Machine: machine_formatter,
        PurchasedMachine: purchased_machine_formatter,
        Withdrawal: withdrawal_formatter,
        Deposit: deposit_formatter,
        Income: income_formatter,
    }
)
