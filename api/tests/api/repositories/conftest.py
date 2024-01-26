import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.api.conftest import async_session_maker
from src.database.models import User
from src.repositories.UserRepository import UserRepository
from src.repositories.MasterReferralRepository import MasterReferralRepository


async def save_referral(session: AsyncSession, master: User, referral_data):
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
            "password_hash": "test_password_hash",
            "affiliate_code": f"{master.affiliate_code}{i}",
        }
        referral = await save_referral(session, master, referral_data)
        referrals.append(referral)
    return referrals


@pytest.fixture(scope="session", autouse=True)
async def create_users(setup_db):
    async with async_session_maker() as session:
        initial_data = [
            {
                "username": "admin1",
                "email": "admin1@admin.com",
                "password_hash": "test_password_hash",
                "affiliate_code": "1",
            },
            {
                "username": "admin2",
                "email": "admin2@admin.com",
                "password_hash": "test_password_hash",
                "affiliate_code": "2",
            },
            {
                "username": "admin3",
                "email": "admin3@admin.com",
                "password_hash": "test_password_hash",
                "affiliate_code": "3",
            },
        ]

        users = [await UserRepository(session).add(data) for data in initial_data]
        for user in users:
            referrals1 = await create_referrals_for_master(session, user, 4)
            for ref1 in referrals1:
                referrals2 = await create_referrals_for_master(session, ref1, 3)
                for ref2 in referrals2:
                    referrals3 = await create_referrals_for_master(session, ref2, 2)
                    for ref3 in referrals3:
                        await create_referrals_for_master(session, ref3, 1)
        await session.commit()
