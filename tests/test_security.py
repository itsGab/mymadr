from jwt import decode

from mymadr.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from mymadr.settings import settings


def test_jwt():
    data = {"test": "test"}
    token = create_access_token(data)
    decoded = decode(
        jwt=token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


def test_password():
    password = "senha123"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
