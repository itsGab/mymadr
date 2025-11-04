from http import HTTPStatus
from time import sleep


def test_create_new_user(client):
    json_input = {
        "username": "new_user",
        "email": "new@mail.com",
        "senha": "password",
    }
    json_output = {
        "id": 1,
        "username": "new_user",
        "email": "new@mail.com",
    }
    response = client.post(
        "/conta/",
        json=json_input,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == json_output


def test_create_username_conflict(client, user):
    json_input = {
        "username": user.username,
        "email": "new@mail.com",
        "senha": "password",
    }
    response = client.post("/conta/", json=json_input)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"message": "Nome de usuário já consta no MADR"}


def test_create_email_conflict(client, user):
    json_input = {
        "username": "new_user",
        "email": user.email,
        "senha": "password",
    }
    response = client.post("/conta/", json=json_input)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"message": "Email já consta no MADR"}


def test_update_all_fields(client, user, token):
    json_input = {
        "username": "updated",
        "email": "updated@mail.com",
        "senha": "updated",
    }
    json_output = {"username": "updated", "email": "updated@mail.com", "id": 1}
    response = client.put(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_update_username(client, user, token):
    json_input = {
        "username": "updated",
    }
    json_output = {"username": "updated", "email": user.email, "id": 1}
    response = client.put(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_update_email(client, user, token):
    json_input = {
        "email": "updated@mail.com",
    }
    json_output = {
        "username": user.username,
        "email": "updated@mail.com",
        "id": user.id,
    }
    response = client.put(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_update_password(client, user, token):
    json_input = {
        "senha": "updated",
    }
    json_output = {
        "username": user.username,
        "email": user.email,
        "id": user.id,
    }
    response = client.put(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.json() == json_output
    assert response.status_code == HTTPStatus.OK
    # FIXME adicionar passo para verificar se loga


def test_update_integrity_error_username(client, user, other_user, token):
    json_input = {
        "username": other_user.username,
    }
    response = client.put(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"message": "Nome de usuário já consta no MADR"}


def test_update_integrity_error_email(client, user, other_user, token):
    json_input = {
        "email": other_user.email,
    }
    response = client.put(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"message": "Email já consta no MADR"}


def test_delete_user(client, user, token):
    response = client.delete(
        f"/conta/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Conta deletada com sucesso"}


def test_update_unauthorized_wrong_id(client, user, other_user, token):
    json_input = {"username": "updated"}
    response = client.put(
        f"/conta/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_delete_unauthorized_wrong_id(client, user, other_user, token):
    response = client.delete(
        f"/conta/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_update_unauthorized_not_authenticated(client, user):
    json_input = {"username": "updated"}
    response = client.put(f"/conta/{user.id}", json=json_input)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_delete_unauthorized_not_authenticated(client, user):
    response = client.delete(f"/conta/{user.id}")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_token(client, user):
    response = client.post(
        "/token/",
        data={"username": user.email, "password": user.clean_password},
    )
    assert response.json()["token_type"] == "bearer"
    assert response.status_code == HTTPStatus.OK


def test_token_invalid_email(client, user):
    response = client.post(
        "/token/",
        data={"username": "invalid@mail.com", "password": user.clean_password},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"message": "Email ou senha incorretos"}


def test_token_invalid_password(client, user):
    response = client.post(
        "/token/",
        data={"username": user.email, "password": "invalid"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"message": "Email ou senha incorretos"}


def test_refresh_token(client, token):
    sleep(1)
    response = client.post(
        "/refresh-token", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    assert token != response.json()["access_token"]


def test_refresh_token_unauthorized(client):
    response = client.post("/refresh-token")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_account_update_empty_fields(): ...  # TODO implementar teste
