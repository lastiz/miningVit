import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.UserRepository import UserRepository
from src.utils.security import SecurityHasher


@pytest.mark.parametrize(
    "status_code",
    [200],
)
async def test_user_GET(
    client: TestClient,
    login,
    status_code,
):
    token: str = login(client, username="registeruser1", password="password1")
    response = client.get(url="/api/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status_code
    if status_code == 200:
        data: dict = response.json()
        assert data["username"] == "registeruser1"
        assert data["email"] == "register1@user.com"
        assert data["email_allowed"] == True
        assert data["telegram"] == None
        assert isinstance(data["affiliate_code"], str)
        assert data["is_active"] == True
        assert data["ip_address"] == None
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)


@pytest.mark.parametrize(
    "password, new_password, status_code",
    [
        (
            "password1",
            "password2",
            200,
        ),
        (
            "password1",
            "password123",
            401,
        ),
        (
            None,
            "password",
            401,
        ),
        (
            "password2",
            None,
            422,
        ),
        (
            "password2",
            "",
            422,
        ),
        (
            "password2",
            None,
            422,
        ),
        (
            "password2",
            "12345",
            422,
        ),
        (
            "password2",
            "12345678901234567",
            422,
        ),
        (
            "password2",
            "password1",
            200,
        ),
    ],
)
async def test_change_password(
    client: TestClient,
    session: AsyncSession,
    login,
    password,
    new_password,
    status_code,
):
    token: str = login(client, username="registeruser1", password=password)
    response = client.post(
        url="/api/user/change_password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "password": password,
            "new_password": new_password,
        },
    )
    assert response.status_code == status_code
    if status_code == 200:
        user = await UserRepository(session).get_by_name("registeruser1")
        assert user
        assert SecurityHasher.verify_password(new_password, user.password_hash)
        assert response.json()["result"] == "password was changed"
