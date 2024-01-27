import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.UserRepository import UserRepository
from src.utils.security import SecurityHasher


@pytest.mark.parametrize(
    "data, status_code",
    [
        (
            {
                "username": "registeruser1",
                "email": "register1@user.com",
                "password": "test_password",
                "affiliate_code": "1",
            },
            201,
        ),
        (
            {
                "username": "registeruser2",
                "email": "register2@user.com",
                "password": "test_password",
                "affiliate_code": "1",
            },
            201,
        ),
        (
            {
                "username": "registeruser1pop3pop3pop3",  # length more than 16
                "email": "register13@user.com",
                "password": "test_password",
                "affiliate_code": "12",
            },
            422,
        ),
        (
            {
                "username": "registeruser1",  # same username
                "email": "register4@user.com",
                "password": "test_password",
                "affiliate_code": "123",
            },
            422,
        ),
        (
            {
                "username": "registeruser5",
                "email": "register1@user.com",  # same email
                "password": "test_password",
                "affiliate_code": "123",
            },
            422,
        ),
        (
            {
                "username": "registeruser6",  # no password
                "email": "register7@user.com",
                "affiliate_code": "123",
            },
            422,
        ),
        (
            {
                "username": "registeruser8",  # no affiliate code
                "email": "register8@user.com",
                "password": "test_password",
            },
            422,
        ),
        (
            {
                "username": "registeruser9",  # no email
                "password": "test_password",
                "affiliate_code": "1",
            },
            422,
        ),
        (
            {
                "email": "register10@user.com",  # no username
                "password": "test_password",
                "affiliate_code": "1",
            },
            422,
        ),
    ],
)
async def test_register(
    client: TestClient,
    session: AsyncSession,
    data: dict,
    status_code,
):
    response = client.post(
        "/auth/register",
        json={
            "username": data.get("username"),
            "email": data.get("email"),
            "password": data.get("password"),
            "affiliate_code": data.get("affiliate_code"),
        },
    )
    assert response.status_code == status_code
    if status_code == 201:
        user = await UserRepository(session).get_by_name(data["username"])
        assert user
        assert response.json()["username"] == data["username"]
        assert response.json()["email"] == data["email"]
        assert response.json()["affiliate_code"] == user.affiliate_code


@pytest.mark.parametrize(
    "data, status_code",
    [
        (
            {
                "username": "fake_user",
                "password": "asdffgh",
            },
            401,
        ),
        (
            {
                "username": "registeruser1",
                "password": "test_password",
            },
            200,
        ),
        (
            {
                "username": "registeruser2",
                "password": "test_password",
            },
            200,
        ),
        (
            {
                "username": "registeruser2",
            },
            422,
        ),
        (
            {
                "password": "test_password",
            },
            422,
        ),
        (
            {},
            422,
        ),
    ],
)
async def test_token(client: TestClient, data, status_code):
    response = client.post(
        "/auth/token",
        data={
            "username": data.get("username"),
            "password": data.get("password"),
        },
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert isinstance(response.json()["access_token"], str)
        assert len(response.json()["access_token"].split(".")) == 3
        assert response.json()["token_type"] == "bearer"


@pytest.mark.parametrize(
    "status_code, result",
    [
        (
            200,
            "email was send",
        ),
        (
            200,
            "email was send",
        ),
    ],
)
async def test_verification_GET(client: TestClient, status_code, result, login):
    token: str = login(client, username="registeruser1", password="test_password")
    response = client.get(
        url="/auth/verification", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status_code
    assert response.json()["result"] == result


@pytest.mark.parametrize(
    "code, status_code",
    [
        ("11112", 400),
        ("11111111111111111", 400),
        ("1", 400),
        (None, 422),
        ("", 400),
        ("11111", 200),
        ("11111", 200),
    ],
)
async def test_verification_POST(
    client: TestClient,
    code,
    status_code,
    login,
):
    token: str = login(client, username="registeruser1", password="test_password")
    response = client.post(
        "/auth/verification",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": code},
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()["result"] == "user was activated"


@pytest.mark.parametrize(
    "email, status_code",
    [
        ("", 405),
        (None, 400),
        ("example@", 400),
        ("register1@user.com", 200),
    ],
)
async def test_reset_password_GET(
    client: TestClient,
    email: str,
    status_code: int,
):
    response = client.get(url=f"/auth/reset_password/{email}")
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()["result"] == "email was send"


@pytest.mark.parametrize(
    "email, password, reset_token, status_code",
    [
        ("register1@user.com", "password1", "11112", 400),
        ("register1@user.vip", "password1", "11111", 400),
        ("register1@user.com", None, "11111", 422),
        ("register1@user.com", "", "11111", 422),
        (None, "password1", "11111", 422),
        ("", "password1", "11111", 422),
        ("register1@user.com", "password1", "", 400),
        ("register1@user.com", "password1", None, 422),
        ("register1@user.com", "password1", "11111", 200),
        ("register1@user.com", "password1", "11111", 400),
    ],
)
async def test_reset_password_POST(
    client: TestClient,
    session: AsyncSession,
    email: str,
    password: str,
    reset_token: str,
    status_code: int,
):
    user_repository = UserRepository(session)
    response = client.post(
        url="/auth/reset_password/",
        json={
            "email": email,
            "password": password,
            "reset_token": reset_token,
        },
    )

    assert response.status_code == status_code
    if status_code == 200:
        user = await user_repository.get_by_email(email)
        assert user
        assert SecurityHasher.verify_password(password, user.password_hash)
