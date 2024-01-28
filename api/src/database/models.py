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


class Base(DeclarativeBase, ReprMixin):
    __abstract__: bool = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}"


class TimeMixin(DeclarativeBase):
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


class User(Base, TimeMixin):
    __repr_attrs__ = ["username", "email", "is_active", "ip_address"]

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
    balance: Mapped["Finance"] = relationship(
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
    __repr_attrs__ = ["user_id", "machine_id", "activated_time"]

    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[int] = mapped_column(BIGINT(unsigned=True))
    income: Mapped[int] = mapped_column(BIGINT(unsigned=True))
    affiliate_income: Mapped[int] = mapped_column(BIGINT(unsigned=True))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(back_populates="balance")


class Machine(Base):
    __repr_attrs__ = ["title", "coin", "income"]

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    coin: Mapped[str] = mapped_column(String(16))
    income: Mapped[int]

    purchased: Mapped[list["PurchasedMachine"]] = relationship(
        back_populates="machine",
        cascade="all, delete",
        passive_deletes=True,
    )


class PurchasedMachine(Base, TimeMixin):
    __tablename__: declared_attr | str = "purchased_machine"
    __repr_attrs__ = ["user_id", "machine_id", "activated_time"]

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machine.id"), primary_key=True)
    activated_time: Mapped[datetime | None] = mapped_column(DateTime)

    machine: Mapped["Machine"] = relationship(back_populates="purchased")
    user: Mapped["User"] = relationship(back_populates="machines")
