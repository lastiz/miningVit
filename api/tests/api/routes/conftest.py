import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_security_hasher(monkeypatch):
    def mock_get_timed_hash(*args, **kwargs):
        return "11111"

    monkeypatch.setattr(
        "utils.security.SecurityHasher.get_timed_hash", mock_get_timed_hash
    )


@pytest.fixture
def login():
    def _login(client: TestClient, username: str, password: str) -> str | None:
        response = client.post(
            "/auth/token",
            data={
                "username": username,
                "password": password,
            },
        )
        if not response.status_code in (200, 201):
            return None
        token: str = response.json()["access_token"]
        return token

    return _login
