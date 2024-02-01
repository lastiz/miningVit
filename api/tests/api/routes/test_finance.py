from typing import Callable
import pytest
from fastapi.testclient import TestClient

from src.utils.enums import IncomeType


@pytest.mark.parametrize(
    "username, password, balance, status_code",
    [
        (
            "admin1",
            "test_password",
            1,
            200,
        ),
        (
            "admin2",
            "test_password",
            2,
            200,
        ),
        (
            "admin3",
            "test_password",
            3,
            200,
        ),
    ],
)
async def test_get_user_finance_info(
    client: TestClient,
    login: Callable[[TestClient, str, str], None | str],
    username: str,
    password: str,
    balance: int,
    status_code: int,
):
    token = login(client, username, password)
    assert token
    response = client.get(
        url="/api/finance",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status_code
    assert response.json()["balance"] == balance


@pytest.mark.parametrize(
    "username, password, deposit_count, deposit_amount, status_code",
    [
        (
            "admin1",
            "test_password",
            1,
            1,
            200,
        ),
        (
            "admin2",
            "test_password",
            2,
            2,
            200,
        ),
        (
            "admin3",
            "test_password",
            3,
            3,
            200,
        ),
        (
            "user11",
            "test_password",
            0,
            0,
            200,
        ),
    ],
)
async def test_get_user_deposits(
    client: TestClient,
    login: Callable[[TestClient, str, str], None | str],
    username: str,
    password: str,
    deposit_count: int,
    deposit_amount: int,
    status_code: int,
):
    token = login(client, username, password)
    assert token
    response = client.get(
        url="/api/finance/deposit",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status_code
    assert len(response.json()["deposits"]) == deposit_count
    for deposit in response.json()["deposits"]:
        assert deposit["amount"] == deposit_amount
        assert deposit["platform"] == "test_platform"


@pytest.mark.parametrize(
    "username, password, withdrawal_count, withdrawal_amount, status_code",
    [
        (
            "admin1",
            "test_password",
            1,
            1,
            200,
        ),
        (
            "admin2",
            "test_password",
            2,
            2,
            200,
        ),
        (
            "admin3",
            "test_password",
            3,
            3,
            200,
        ),
        (
            "user11",
            "test_password",
            0,
            0,
            200,
        ),
    ],
)
async def test_get_user_withdrawals(
    client: TestClient,
    login: Callable[[TestClient, str, str], None | str],
    username: str,
    password: str,
    withdrawal_count: int,
    withdrawal_amount: int,
    status_code: int,
):
    token = login(client, username, password)
    assert token
    response = client.get(
        url="/api/finance/withdrawal",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status_code
    assert len(response.json()["withdrawals"]) == withdrawal_count
    for deposit in response.json()["withdrawals"]:
        assert deposit["amount"] == withdrawal_amount
        assert deposit["wallet"] == "test_wallet"


@pytest.mark.parametrize(
    "username, password, income_count, income_amount, status_code",
    [
        (
            "admin1",
            "test_password",
            1,
            1,
            200,
        ),
        (
            "admin2",
            "test_password",
            2,
            2,
            200,
        ),
        (
            "admin3",
            "test_password",
            3,
            3,
            200,
        ),
        (
            "user11",
            "test_password",
            0,
            0,
            200,
        ),
    ],
)
async def test_get_user_incomes(
    client: TestClient,
    login: Callable[[TestClient, str, str], None | str],
    username: str,
    password: str,
    income_count: int,
    income_amount: int,
    status_code: int,
):
    token = login(client, username, password)
    assert token
    response = client.get(
        url="/api/finance/income",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status_code
    assert len(response.json()["incomes"]) == income_count
    for deposit in response.json()["incomes"]:
        assert deposit["amount"] == income_amount
        assert deposit["type"] == IncomeType.BONUS
