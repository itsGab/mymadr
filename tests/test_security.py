from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode

from mymadr.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from mymadr.settings import settings


def test_jwt_success():
    data = {"test": "test"}
    token = create_access_token(data)
    decoded = decode(
        jwt=token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )
    assert decoded["test"] == data["test"]
    assert "exp" in decoded


def test_jwt_invalid_token(client, user):
    response = client.delete(
        "/conta/1", headers={"Authorization": "Bearer invalid token"}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_get_current_user_exception_decode_error_unauthorized(session):
    # test case for JWT token error (or decode error)
    with pytest.raises(HTTPException) as exc:
        get_current_user(session, token="invalid-token")
    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == "Não autorizado"


def test_current_user_exception_user_is_none_unauthorized(session):
    # test case for user not found in the database
    data_no_username = {"sub": "test@test"}
    token = create_access_token(data_no_username)
    with pytest.raises(HTTPException) as exc:
        get_current_user(session, token)
    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == "Não autorizado"


def test_current_user_exception_no_username_unauthorized(session):
    # test case for missing 'sub' in the payload
    data_user_none = {"test": "test"}
    token = create_access_token(data_user_none)
    with pytest.raises(HTTPException) as exc:
        get_current_user(session, token)
    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == "Não autorizado"


def test_password_success():
    password = "password123"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
