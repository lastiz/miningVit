import pytest
from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time

from src.repositories.UserRepository import UserRepository
from src.database.models import User


def assert_dict_values_equal_obj_props(dict_: dict, obj: object):
    for k, v in dict_.items():
        assert v == getattr(obj, k)


class TestUserRepository:
    @pytest.mark.parametrize(
        "data, expectation",
        [
            (
                {
                    "username": "testuser1",
                    "email": "test1@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "101",
                },
                does_not_raise(),
            ),
            (
                {
                    "username": "testuser2",
                    "email": "test2@test.com",
                    "password_hash": "test_pfsdfassword_hash",
                    "affiliate_code": "102",
                },
                does_not_raise(),
            ),
            (
                {
                    "username": "testuser3",
                    "email": "test3@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "103",
                },
                does_not_raise(),
            ),
            (
                {
                    "email": "test4@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "104",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "username": "testuser5",
                    "email": "test5@test.com",
                    "password_hash": "test_password_hash",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "username": "testuser6",
                    "email": "test6@test.com",
                    "affiliate_code": "105",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "username": "testuse7",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "106",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "username": "testuser8",
                    "email": "test1@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "107",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "username": "testuser1",
                    "email": "test9@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "108",
                },
                pytest.raises(IntegrityError),
            ),
        ],
    )
    async def test_add(self, data, expectation, session: AsyncSession):
        user_repository = UserRepository(session)
        with expectation:
            user = await user_repository.add(data)
            assert hasattr(user, "id")
            assert not getattr(user, "is_admin")
            assert not getattr(user, "is_active")
            assert getattr(user, "email_allowed")
            assert_dict_values_equal_obj_props(data, user)
            await session.commit()

    @pytest.mark.parametrize(
        "data",
        [
            {
                "username": "admin",
                "email": "admin@admin.com",
                "password_hash": "test_password_hash",
                "affiliate_code": "1111111111",
                "is_admin": True,
            },
        ],
    )
    async def test_add_admin(self, data, session: AsyncSession):
        user_repository = UserRepository(session)
        user = await user_repository.add(data)
        assert_dict_values_equal_obj_props(data, user)
        assert getattr(user, "is_admin")

    async def test_delete(self, session: AsyncSession):
        user_repository = UserRepository(session)
        await user_repository.add(
            {
                "username": "delete_user",
                "email": "delete@test.com",
                "password_hash": "test_password_hash",
                "affiliate_code": "123123123",
            }
        )
        await session.commit()
        user_id = await session.scalar(
            select(User.id).where(User.username == "delete_user")
        )
        assert user_id
        await user_repository.delete(id=user_id)
        await session.commit()
        assert await user_repository.get_by_id(user_id) is None

    async def test_update(self, session: AsyncSession):
        user_repository = UserRepository(session)
        initial_user_data = {
            "username": "to_update_user",
            "email": "to_update_user@test.com",
            "password_hash": "test_password_hash",
            "affiliate_code": "123123123",
        }
        user = await user_repository.add(initial_user_data)
        await session.commit()
        time.sleep(1)
        old_field_updated_at = user.updated_at
        await user_repository.update(
            user.id,
            {
                "username": "updated_username",
                "email": "updated_email@test.com",
                "updated_at": user.updated_at,
            },
        )
        await session.commit()
        assert user
        assert user.email == "updated_email@test.com"
        assert user.username == "updated_username"
        assert user.updated_at > old_field_updated_at

    async def test_get_by_id(self, session):
        user_repository = UserRepository(session)
        user = await user_repository.get_by_id(2)
        assert user
        assert user.id == 2

    async def test_get_by_email(self, session):
        user_repository = UserRepository(session)
        user = await user_repository.get_by_email("admin1@admin.com")
        assert user
        assert user.email == "admin1@admin.com"

    async def test_get_by_username(self, session):
        user_repository = UserRepository(session)
        user = await user_repository.get_by_name("testuser1")
        assert user
        assert user.username == "testuser1"

    async def test_get_by_affiliate_code(self, session):
        user_repository = UserRepository(session)
        await user_repository.add(
            {
                "username": "testuser10",
                "email": "test10@test.com",
                "password_hash": "test_password_hash",
                "affiliate_code": "666",
            }
        )
        await session.commit()
        user = await user_repository.get_by_affiliate_code("666")
        assert user
        assert user.affiliate_code == "666"

    async def test_check_existance_by(self, session):
        user_repository = UserRepository(session)
        is_exists = await user_repository.check_existance_by(affiliate_code="666")
        assert is_exists
        is_exists2 = await user_repository.check_existance_by(
            affiliate_code="fake_code"
        )
        assert not is_exists2

    async def test_list(self, session):
        user_repository = UserRepository(session)
        users = await user_repository.list()
        assert len(users) > 1
        users = await user_repository.list(affiliate_code="666")
        assert len(users) == 1

    @pytest.mark.parametrize(
        "level, expect_len, expectation",
        [
            (None, None, pytest.raises(TypeError)),
            ("1", None, pytest.raises(TypeError)),
            (0, 0, does_not_raise()),
            (1, 4, does_not_raise()),
            (2, 12, does_not_raise()),
            (3, 24, does_not_raise()),
            (4, 24, does_not_raise()),
            (5, 0, does_not_raise()),
        ],
    )
    async def test_get_referrals(self, level, expectation, expect_len, session):
        user_repository = UserRepository(session)
        master = await user_repository.get_by_name("admin1")
        assert master
        with expectation:
            referrals = await user_repository.get_referrals(master, level=level)
            assert len(referrals) == expect_len

    @pytest.mark.parametrize(
        "username, master_username",
        [
            ("user11", "admin1"),
            ("user12", "admin1"),
            ("user13", "admin1"),
            ("user21", "admin2"),
            ("user32", "admin3"),
            ("user121", "user12"),
        ],
    )
    async def test_get_master(self, session, username, master_username):
        user_repository = UserRepository(session)
        referral = await user_repository.get_by_name(username)
        assert referral
        master = await user_repository.get_master(referral)
        assert master
        assert master.username == master_username
