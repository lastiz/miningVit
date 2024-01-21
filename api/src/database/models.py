from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from sqlalchemy import String, ForeignKey, DateTime, DefaultClause
from sqlalchemy.sql import func, text, false, true
from datetime import datetime


class Base(DeclarativeBase):
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
    master_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    referral_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


class User(Base, TimeMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    # Register information
    username: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email_allowed: Mapped[bool] = mapped_column(server_default=true())
    telegram: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(516))
    is_admin: Mapped[bool] = mapped_column(server_default=false())
    is_active: Mapped[bool] = mapped_column(server_default=false())
    affiliate_code: Mapped[str] = mapped_column(String(10), unique=True, index=True)

    # Admin info
    note: Mapped[str | None] = mapped_column(String(1024))
