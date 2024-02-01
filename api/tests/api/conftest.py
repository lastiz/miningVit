from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from src.database.db import engine
from fastapi.testclient import TestClient
from src.main import app

from src.database.models import Base
from src.config import settings
from src.repositories.UserRepository import UserRepository
from src.repositories.MasterReferralRepository import MasterReferralRepository
from src.repositories.finance_repository import FinanceRepository
from src.database.models import User
from src.utils.enums import IncomeType
from src.utils.security import SecurityHasher


engine_test = create_async_engine(settings.DB_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    bind=engine_test,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    async def mock_send_account_verification_email(*args, **kwargs):
        return True

    async def mock_send_reset_password_email(*args, **kwargs):
        return True

    monkeypatch.setattr(
        "services.email_service.EmailService.send_account_verification_email",
        mock_send_account_verification_email,
    )
    monkeypatch.setattr(
        "services.email_service.EmailService.send_reset_password_email",
        mock_send_reset_password_email,
    )


@pytest.fixture(autouse=True)
def mock_redis_service(monkeypatch):
    async def mock_save_email_lock(*args, **kwargs):
        return True

    async def mock_email_lock_exists(*args, **kwargs):
        return False

    monkeypatch.setattr(
        "services.redis_service.RedisService.save_email_lock",
        mock_save_email_lock,
    )
    monkeypatch.setattr(
        "services.redis_service.RedisService.email_lock_exists",
        mock_email_lock_exists,
    )


@pytest.fixture(autouse=True)
def mock_user_service(monkeypatch):
    def mock_create_verification_code(*args, **kwargs):
        return "11111"

    monkeypatch.setattr(
        "services.user_service.UserService.create_verification_code",
        mock_create_verification_code,
    )


@pytest.fixture(scope="session")
async def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True, scope="session")
async def setup_db():
    """Create all tables in db and then delete all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# -------------------- DATA CREATION FOR DATABASE -------------------#

TEST_PASSWORD_HASH = SecurityHasher.get_password_hash("test_password")


async def save_referral(session: AsyncSession, master: User, referral_data) -> User:
    """Saves referral for master for testing purposes

    Args:
        session (AsyncSession): AsyncSession
        master (User): referrer for referral
        referral_data (_type_): data for referral to save

    Returns:
        _type_: User model
    """
    referral = await UserRepository(session).add(referral_data)
    await MasterReferralRepository(session).add(
        {"master_id": master.id, "referral_id": referral.id}
    )
    return referral


async def create_referrals_for_master(session: AsyncSession, master: User, count: int):
    referrals: list[User] = []
    for i in range(1, count + 1):
        referral_data = {
            "username": f"user{master.affiliate_code}{i}",
            "email": f"user{master.affiliate_code}{i}@user.com",
            "password_hash": TEST_PASSWORD_HASH,
            "affiliate_code": f"{master.affiliate_code}{i}",
            "ip_address": "127.0.0.1",
            "is_active": True,
        }
        referral = await save_referral(session, master, referral_data)
        await FinanceRepository(session).add({"user_id": referral.id})
        referrals.append(referral)
    return referrals


@pytest.fixture(autouse=True, scope="session")
async def create_data_for_db(setup_db):
    """Creates some data for testing

    Args:
        setup_db (_type_): pytest fixture to ensure this fixture runs after setup_db
    """
    # FOR USER REPOSITORY
    initial_user_data = [
        {
            "username": "admin1",
            "email": "admin1@admin.com",
            "password_hash": TEST_PASSWORD_HASH,
            "affiliate_code": "1",
            "ip_address": "127.0.0.1",
            "is_active": True,
        },
        {
            "username": "admin2",
            "email": "admin2@admin.com",
            "password_hash": TEST_PASSWORD_HASH,
            "affiliate_code": "2",
            "ip_address": "127.0.0.1",
            "is_active": True,
        },
        {
            "username": "admin3",
            "email": "admin3@admin.com",
            "password_hash": TEST_PASSWORD_HASH,
            "affiliate_code": "3",
            "ip_address": "127.0.0.1",
            "is_active": True,
        },
    ]
    async with async_session_maker() as session:
        # creation initial users
        users = [await UserRepository(session).add(data) for data in initial_user_data]
        # creation of initial user finance
        for user in users:
            await FinanceRepository(session).add({"user_id": user.id})
        # changing balance according to id for initial users
        for user in users:
            finance_ropsitory = FinanceRepository(session)
            user_finance = await finance_ropsitory.get_user_finance(user.id)
            assert user_finance
            await finance_ropsitory.update(user_finance.id, data={"balance": user.id})
        # transaction creation for initial users
        for user in users:
            await create_test_transactions(
                user,
                session,
                deposit_amount=user.id,
                withdrawal_amount=user.id,  # amounts are equal user.id for testing
                income_amount=user.id,
            )
        # creation of referrals for initial users
        for user in users:
            referrals1 = await create_referrals_for_master(session, user, 4)
            for ref1 in referrals1:
                referrals2 = await create_referrals_for_master(session, ref1, 3)
                for ref2 in referrals2:
                    referrals3 = await create_referrals_for_master(session, ref2, 2)
                    for ref3 in referrals3:
                        await create_referrals_for_master(session, ref3, 1)
        await session.commit()


async def create_test_transactions(
    user: User,
    session: AsyncSession,
    deposit_amount: int,
    withdrawal_amount: int,
    income_amount: int,
):
    """Creates fake deposits, withdrawals and incomes

    Args:
        user (User): obj of User model
        deposit_count (int): amount of deposits
        withdrawal_count (int): amount of withdrawals
        income_count (int): amount of incomes
    """
    finance_repositrory = FinanceRepository(session)

    for _ in range(deposit_amount):
        await finance_repositrory.add_user_deposit(
            user_id=user.id,
            data={
                "amount": user.id,  # amount is equal user id for testing
                "platform": "test_platform",
            },
        )

    for _ in range(withdrawal_amount):
        await finance_repositrory.add_user_withdrawal(
            user_id=user.id,
            data={
                "amount": user.id,  # amount is equal user id for testing
                "wallet": "test_wallet",
            },
        )

    for _ in range(income_amount):
        await finance_repositrory.add_user_income(
            user_id=user.id,
            data={
                "amount": user.id,  # amount is equal user id for testing
                "type": IncomeType.BONUS,
            },
        )
