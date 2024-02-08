from typing import Sequence
from datetime import datetime, timedelta

from database.db import DB
from schemas.machine import MachineSchema, UserMachineSchema
from schemas.user import UserSchema
from schemas.finance import FinanceInfoSchema
from utils.validation_errors import AppError
from utils.enums import MachineCoin
from config import settings


class MachineService:
    def __init__(self, db: DB) -> None:
        self.db = db

    async def get_user_machines(self, user: UserSchema) -> Sequence[UserMachineSchema]:
        db_purchased_machines = await self.db.machines.purchased.list(
            eager=["machine"], user_id=user.id
        )
        return [
            UserMachineSchema.model_validate(machine)
            for machine in db_purchased_machines
        ]

    async def get_all_machines(self) -> Sequence[MachineSchema]:
        db_machines = await self.db.machines.list()
        return [MachineSchema.model_validate(db_machine) for db_machine in db_machines]

    async def activate_user_machine(
        self, user: UserSchema, purchased_machine_id: int
    ) -> None:
        is_owner = await self.db.machines.purchased.is_exists(
            user_id=user.id, id=purchased_machine_id
        )
        if not is_owner:
            raise AppError.MACHINE_NOT_OWNED

        await self.db.machines.purchased.update(
            id=purchased_machine_id,
            data={"activated_time": datetime.now()},
        )

    async def get_machine_by_coin(self, machine_coin: MachineCoin) -> MachineSchema:
        db_machine = await self.db.machines.get_by_filters(coin=machine_coin)
        if db_machine is None:
            raise AppError.MACHINE_NOT_FOUND
        return MachineSchema.model_validate(db_machine)

    async def purchase_machine(
        self, user: UserSchema, machine_coin: MachineCoin
    ) -> None:
        """Creates user_machine association and decrease user balance

        Args:
            user (UserSchema): User that wants to buy machine
            machine_coin (MachineCoin): Enum, represents coin associated with machine

        Raises:
            AppError.MACHINE_ALREADY_PURCHASED: raises if machine with :machine_coin already purchased
            AppError.COULD_NOT_GET_FINANCE: raises if couldn't get user finance object
            AppError.INSUFFICIENT_BALANCE: raises if user's balance is too low
        """
        desired_machine = await self.get_machine_by_coin(machine_coin)

        already_purchased = await self.db.machines.purchased.is_exists(
            user_id=user.id,
            machine_id=desired_machine.id,
        )
        if already_purchased:
            raise AppError.MACHINE_ALREADY_PURCHASED

        db_user_finance = await self.db.finance.get_by_filters(
            user_id=user.id, for_update=True
        )
        if db_user_finance is None:
            raise AppError.COULD_NOT_GET_FINANCE
        user_finance = FinanceInfoSchema.model_validate(db_user_finance)

        if user_finance.balance < desired_machine.price:
            raise AppError.INSUFFICIENT_BALANCE

        await self.db.machines.purchased.add(
            {"user_id": user.id, "machine_id": desired_machine.id}
        )
        user_finance.balance -= desired_machine.price
        await self.db.finance.update(user_finance.id, user_finance.model_dump())

    async def receive_commissions(
        self, user: UserSchema, purchased_machine_id: int
    ) -> None:
        """Updates user Finance.balance accordingly to PurchasedMachine.machine.income

        Args:
            user (UserSchema): user data
            purchased_machine_id (int): id for PurchasedMachine

        Raises:
            AppError.MACHINE_NOT_OWNED: raises if purchased_machine_id is incorrect
            AppError.MACHINE_NOT_ACTIVATED: raises if machine wasn't activated
            AppError.INVALID_REQUEST_TIME: raises if request received too early
        """
        db_purchased_machine = await self.db.machines.purchased.get_by_filters(
            user_id=user.id,
            id=purchased_machine_id,
            eager=["machine"],
            for_update=True,
        )
        if db_purchased_machine is None:
            raise AppError.MACHINE_NOT_OWNED

        purchased_machine = UserMachineSchema.model_validate(db_purchased_machine)
        if purchased_machine.activated_time is None:
            raise AppError.MACHINE_NOT_ACTIVATED

        if datetime.now() - purchased_machine.activated_time < timedelta(
            hours=settings.COMMISSION_HOURS_DELTA
        ):
            raise AppError.INVALID_REQUEST_TIME

        user_finance = FinanceInfoSchema.model_validate(
            await self.db.finance.get_by_filters(user_id=user.id)
        )
        user_finance.balance += purchased_machine.machine.income
        await self.db.finance.update(user_finance.id, user_finance.model_dump())
        purchased_machine.activated_time = None
        await self.db.machines.purchased.update(
            purchased_machine.id, purchased_machine.model_dump(exclude={"machine"})
        )
