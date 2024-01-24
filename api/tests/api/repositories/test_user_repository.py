import pytest
from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
                    "id": 1,
                    "username": "testuser1",
                    "email": "test1@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "1",
                },
                does_not_raise(),
            ),
            (
                {
                    "id": 2,
                    "username": "testuser2",
                    "email": "test2@test.com",
                    "password_hash": "test_pfsdfassword_hash",
                    "affiliate_code": "2",
                },
                does_not_raise(),
            ),
            (
                {
                    "id": 2,
                    "username": "testuser3",
                    "email": "test3@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "3",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "id": 3,
                    "email": "test4@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "4",
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
                    "affiliate_code": "5",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "username": "testuse7",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "6",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "username": "testuser8",
                    "email": "test1@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "7",
                },
                pytest.raises(IntegrityError),
            ),
            (
                {
                    "username": "testuser1",
                    "email": "test9@test.com",
                    "password_hash": "test_password_hash",
                    "affiliate_code": "8",
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
        user_id = await session.scalar(
            select(User.id).where(User.username == "delete_user")
        )
        assert user_id
        await user_repository.delete(id=user_id)
        await session.commit()
        assert await user_repository.get_by_id(user_id) is None

    async def test_update(self, session):
        user_repository = UserRepository(session)
        user = await user_repository.update(
            id=1,
            data={
                "email": "test500@gmail.com",
                "username": "user500",
            },
        )
        assert user
        await session.commit()
        updated_user = await user_repository.get_by_id(user.id)
        assert updated_user
        assert user.email == updated_user.email
        assert user.username == updated_user.username
        assert user.id == updated_user.id
        some_user = await user_repository.get_by_id(2)
        assert some_user
        assert updated_user.username != some_user.username

    async def test_get_by_id(self, session):
        user_repository = UserRepository(session)
        user = await user_repository.get_by_id(2)
        assert user
        assert user.id == 2

    async def test_get_by_email(self, session):
        user_repository = UserRepository(session)
        user = await user_repository.get_by_email("test500@gmail.com")
        assert user
        assert user.email == "test500@gmail.com"

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
        is_exists = await user_repository.check_existance_by(
            affiliate_code="666"
        )
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