import enum


class PrintableEnum(enum.Enum):
    def __str__(self) -> str:
        return str(self.value)


@enum.unique
class TransactionStatus(str, PrintableEnum):
    NEW = "new"
    PENDING = "pending"
    COMPLETED = "completed"


@enum.unique
class IncomeType(str, PrintableEnum):
    BONUS = "bonus"
    AFFILIATE = "affiliate"
    COMMISSION = "commission"


@enum.unique
class MachineCoin(str, PrintableEnum):
    LTC = "LTC"
    ETC = "ETC"
    PIRL = "PIRL"
    BTC = "BTC"
    ZEN = "ZEN"
    ZEC = "ZEC"
    BTCD = "BTCD"
    PPC = "PPC"
    BCX = "BCX"
