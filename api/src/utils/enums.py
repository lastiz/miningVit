import enum


@enum.unique
class TransactionStatus(str, enum.Enum):
    NEW = "new"
    PENDING = "pending"
    COMPLETED = "completed"


@enum.unique
class IncomeType(str, enum.Enum):
    BONUS = "bonus"
    AFFILIATE = "affiliate"
    M1 = "m1"
    M2 = "m2"
    M3 = "m3"
    M4 = "m4"
    M5 = "m5"
    M6 = "m6"
    M7 = "m7"
    M8 = "m8"
    M9 = "m9"
