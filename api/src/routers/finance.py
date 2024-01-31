from typing import Annotated
from fastapi import APIRouter, Depends

from database.db import DB, get_db
from schemas.user import UserSchema
from dependencies.auth import get_current_active_user
from services.finance_service import FinanceService
from schemas.finance import (
    FinanceInfoSchema,
    DepositsSchema,
    WithdrawalsSchema,
    IncomesSchema,
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


@router.get("/incomes")
async def get_user_incomes(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db: Annotated[DB, Depends(get_db)],
) -> IncomesSchema:
    return await FinanceService(db).get_user_incomes(current_user)
