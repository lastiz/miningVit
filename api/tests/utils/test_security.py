from typing import Any
import pytest
from contextlib import nullcontext as does_not_raise

from src.utils.security import JWTAuthController, SecurityHasher


class TestSecurityHasher:
    hasher = SecurityHasher()
    _params = [0, 1, None, "123", 1.3, object, "username", "", "a", "qwer" * 100]
    _unique_passwords = ["", "password", "1234", b"pass123", "41dggd".encode()]
    _same_passwords = ["password", "password", "password", "password", "password"]

    def test_timed_hash_type_str(self):
        for param in self._params:
            assert isinstance(self.hasher.get_timed_hash(param), str)

    def test_timed_hash_unique(self):
        hashes = [self.hasher.get_timed_hash(param) for param in self._params]
        assert len(self._params) == len(set(hashes))

    def test_timed_hash_len(self):
        for param in self._params:
            assert 64 == len(self.hasher.get_timed_hash(param))

    @pytest.mark.parametrize(
        "password, expectation",
        [
            ("", does_not_raise()),
            ("password", does_not_raise()),
            ("1234", does_not_raise()),
            (b"pass", does_not_raise()),
            ("lolkek123".encode(), does_not_raise()),
            (123456789, pytest.raises(Exception)),
            (123.545, pytest.raises(Exception)),
        ],
    )
    def test_get_password_hash_type_str(self, password, expectation):
        with expectation:
            assert isinstance(self.hasher.get_password_hash(password), str)

    def test_get_password_hash_unique(self):
        hashes = [
            self.hasher.get_password_hash(password)
            for password in self._unique_passwords
        ]
        assert len(hashes) == len(set(hashes))

    def test_get_password_hash_same_passwords(self):
        hashes = set()
        for password in self._same_passwords:
            hashes.add(self.hasher.get_password_hash(password))
        assert len(hashes) == 5

    @pytest.mark.parametrize(
        "password",
        [
            "",
            "password",
            "pass",
            "123",
            b"lokek",
            "poplol".encode(),
            "qwer1234" * 100,
        ],
    )
    def test_get_password_hash_len(self, password):
        assert len(self.hasher.get_password_hash(password)) == 60

    @pytest.mark.parametrize(
        "password",
        [
            "",
            "password",
            "pass",
            "123",
            b"lokek",
            "poplol".encode(),
        ],
    )
    def test_verify_password(self, password):
        password_hash = self.hasher.get_password_hash(password)
        assert self.hasher.verify_password(password, password_hash)


class TestJWTAuthController:
    
    @pytest.mark.parametrize(
        "data",
        [
            {
                "username": "testuser",
            },
            {
                "username": "",
            },
            {},
            {
                "username": None,
            },
            {
                "username": 123
            }
        ]
    )
    def test_encode(self, data: dict[str, Any]):
        token = JWTAuthController.encode(**data)
        splitted_token = token.split('.')
        assert len(splitted_token) == 3
        for piece in splitted_token:
            assert isinstance(piece, str)

    @pytest.mark.parametrize(
        "data",
        [
            {
                "username": "testuser",
            },
            {
                "username": "",
            },
            {},
            {
                "username": None,
            },
            {
                "username": 123
            }
        ]
    )
    def test_decode(self, data: dict[str, Any]):
        token = JWTAuthController.encode(**data)
        decoded_token = JWTAuthController.decode(token)
        assert "exp" in decoded_token
        decoded_token.pop("exp")
        assert decoded_token == data
