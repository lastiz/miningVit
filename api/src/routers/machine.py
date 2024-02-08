from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Query
from database.db import DB, get_db

from dependencies.auth import get_current_active_user
from schemas.user import UserSchema
from schemas.machine import MachineSchema, UserMachineSchema
from schemas.common import ResultSchema
from services.machine_service import MachineService
from utils.enums import MachineCoin


router = APIRouter(tags=["Machine operations"])


@router.get("")
async def get_all_machines(
    _: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
) -> Sequence[MachineSchema]:
    return await MachineService(db).get_all_machines()


@router.get("/owned")
async def get_owned_machines(
    current_active_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
) -> Sequence[UserMachineSchema]:
    return await MachineService(db).get_user_machines(current_active_user)


@router.post("/owned", description="Purchase COIN specific machine")
async def create_purchased_machine(
    current_active_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
    machine_coin: Annotated[MachineCoin, Query()],
) -> ResultSchema:
    await MachineService(db).purchase_machine(current_active_user, machine_coin)
    await db.commit()
    return ResultSchema(result="machine was purchased")


@router.patch("/owned/{purchased_machine_id}")
async def activate_purchased_machine(
    current_active_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
    purchased_machine_id: int,
) -> ResultSchema:
    await MachineService(db).activate_user_machine(
        current_active_user,
        purchased_machine_id,
    )
    await db.commit()
    return ResultSchema(result="machine was activated")


@router.get("/owned/{purchased_machine_id}/receive_commissions")
async def receive_machine_commissions(
    current_active_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
    purchased_machine_id: int,
) -> ResultSchema:
    await MachineService(db).receive_commissions(
        current_active_user, purchased_machine_id
    )
    await db.commit()
    return ResultSchema(result="commissions received")
