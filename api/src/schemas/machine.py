from datetime import datetime

from .base import Base


class MachineSchema(Base):
    id: int
    title: str
    coin: str
    income: int
    price: int


class UserMachineSchema(Base):
    id: int
    activated_time: datetime | None
    machine: MachineSchema
