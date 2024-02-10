from typing import Annotated
from fastapi import APIRouter, Depends

from database.db import DB, get_db
from schemas.user import UserSchema
from dependencies.auth import get_current_active_user
from services.finance_service import FinanceService
from schemas.common import ResultSchema
from schemas.finance import (
    FinanceInfoSchema,
    DepositsSchema,
    WithdrawalsSchema,
    IncomesSchema,
    WithdrawInSchema,
    ChangeWalletSchema,
)


router = APIRouter(tags=["Finance operations"])


@router.get("")
async def get_user_finance_info(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
) -> FinanceInfoSchema:
    return await FinanceService(db).get_user_finance_info(current_user)


@router.get("/deposit")
async def get_user_deposits(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
) -> DepositsSchema:
    return await FinanceService(db).get_user_deposits(current_user)


@router.get("/withdrawal")
async def get_user_withdrawals(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
) -> WithdrawalsSchema:
    return await FinanceService(db).get_user_withdrawals(current_user)


@router.get("/income")
async def get_user_incomes(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
) -> IncomesSchema:
    return await FinanceService(db).get_user_incomes(current_user)


@router.post("/withdraw", status_code=201)
async def withdraw_funds(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
    withdraw_data: WithdrawInSchema,
) -> ResultSchema:
    await FinanceService(db).withdraw_funds(current_user, withdraw_data.amount)
    await db.commit()
    return ResultSchema(result="withdrawal was accepted")


@router.post("/wallet")
async def change_wallet(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
    wallet_data: ChangeWalletSchema,
) -> ResultSchema:
    await FinanceService(db).change_wallet(current_user, wallet_data.wallet)
    await db.commit()
    return ResultSchema(result="wallet was changed")
