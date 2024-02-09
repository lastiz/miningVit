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
    COMMISSION = "commission"


@enum.unique
class MachineCoin(str, enum.Enum):
    LTC = "LTC"
    ETC = "ETC"
    PIRL = "PIRL"
    BTC = "BTC"
    ZEN = "ZEN"
    ZEC = "ZEC"
    BTCD = "BTCD"
    PPC = "PPC"
    BCX = "BCX"
