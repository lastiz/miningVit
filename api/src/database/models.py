from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    declared_attr,
    relationship,
)
from sqlalchemy import String, ForeignKey, DateTime, DefaultClause
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func, text, false, true
from datetime import datetime

from utils.repr import ReprMixin
from utils.enums import TransactionStatus, IncomeType, MachineCoin


class Base(ReprMixin, DeclarativeBase):
    __abstract__: bool = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}"


class TimeMixin:
    __abstract__: bool = True
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=DefaultClause(
            text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        ),
    )


class MasterReferral(Base):
    __tablename__: declared_attr | str = "master_referral"
    __repr_attrs__ = ["master_id", "referral_id"]

    master_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    referral_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


class User(TimeMixin, Base):
    __repr_attrs__ = ["id", "username", "email", "is_active", "ip_address"]

    id: Mapped[int] = mapped_column(primary_key=True)
    # Register information
    username: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email_allowed: Mapped[bool] = mapped_column(server_default=true())
    telegram: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(516))
    affiliate_code: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    is_admin: Mapped[bool] = mapped_column(server_default=false())
    is_active: Mapped[bool] = mapped_column(server_default=false())
    ip_address: Mapped[str] = mapped_column(String(15), nullable=True)
    last_online: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    # Admin info
    note: Mapped[str | None] = mapped_column(String(1024))

    # ADDITIONAL RELATIONSHIPS
    finance: Mapped["Finance"] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    machines: Mapped[list["PurchasedMachine"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )


# ADDITIONAL TABLES
class Finance(Base):
    __repr_attrs__ = ["id", "user_id", "balance", "income", "wallet"]

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet: Mapped[str | None] = mapped_column(String(516))
    balance: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), server_default=text("0")
    )
    income: Mapped[int] = mapped_column(BIGINT(unsigned=True), server_default=text("0"))
    affiliate_income: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), server_default=text("0")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(back_populates="finance")
    deposits: Mapped[list["Deposit"]] = relationship(
        back_populates="finance",
        cascade="all, delete",
        passive_deletes=True,
    )
    withdrawals: Mapped[list["Withdrawal"]] = relationship(
        back_populates="finance",
        cascade="all, delete",
        passive_deletes=True,
    )
    incomes: Mapped[list["Income"]] = relationship(
        back_populates="finance",
        cascade="all, delete",
        passive_deletes=True,
    )


class Machine(Base):
    __repr_attrs__ = ["id", "title", "coin", "income", "price"]

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64), unique=True)
    coin: Mapped[MachineCoin] = mapped_column(unique=True, index=True)
    income: Mapped[int] = mapped_column(BIGINT(unsigned=True))
    price: Mapped[int] = mapped_column(BIGINT(unsigned=True))

    purchased: Mapped[list["PurchasedMachine"]] = relationship(
        back_populates="machine",
        cascade="all, delete",
        passive_deletes=True,
    )


class PurchasedMachine(TimeMixin, Base):
    __tablename__: declared_attr | str = "purchased_machine"
    __repr_attrs__ = ["id", "user_id", "machine_id", "activated_time"]

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    machine_id: Mapped[int] = mapped_column(ForeignKey("machine.id"))
    activated_time: Mapped[datetime | None] = mapped_column(DateTime)

    machine: Mapped["Machine"] = relationship(back_populates="purchased")
    user: Mapped["User"] = relationship(back_populates="machines")


class Transaction:
    __abstract__: bool = True

    id: Mapped[int] = mapped_column(primary_key=True)
    finance_id: Mapped[int] = mapped_column(ForeignKey("finance.id"))
    status: Mapped[TransactionStatus] = mapped_column(default=TransactionStatus.NEW)
    amount: Mapped[int] = mapped_column(BIGINT(unsigned=True))


class Income(Transaction, TimeMixin, Base):
    __repr_attrs__ = ["id", "finance_id", "type", "amount", "status"]

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[IncomeType]

    finance: Mapped["Finance"] = relationship(back_populates="incomes")


class Deposit(Transaction, TimeMixin, Base):
    __repr_attrs__ = ["id", "finance_id", "platform", "amount", "status"]

    platform: Mapped[str] = mapped_column(String(128))

    finance: Mapped["Finance"] = relationship(back_populates="deposits")


class Withdrawal(Transaction, TimeMixin, Base):
    __repr_attrs__ = ["id", "finance_id", "wallet", "amount", "status"]

    wallet: Mapped[str] = mapped_column(String(512))

    finance: Mapped["Finance"] = relationship(back_populates="withdrawals")


class Advert(Base):
    __repr_attrs__ = ["id", "title", "body"]

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    body: Mapped[str] = mapped_column(String(1024))
