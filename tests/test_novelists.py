from http import HTTPStatus

import pytest

from tests.factories import BookFactory


def test_register_novelist_success(client, token):
    json_input = {"nome": "   j.    k. rowling"}
    json_output = {"nome": "j. k. rowling", "id": 1}
    response = client.post(
        "/romancista/",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == json_output


def test_register_novelist_with_existing_novelist_conflict(
    client, novelist, token
):
    json_input = {"nome": novelist.name}
    response = client.post(
        "/romancista/",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"message": "Romancista já consta no MADR"}


def test_get_novelist_by_id_success(client, novelist):
    response = client.get(f"/romancista/{novelist.id}")
    json_output = {"nome": novelist.name, "id": novelist.id}
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_get_novelist_by_id_when_novelist_does_not_exist_not_found(
    client, novelist
):
    response = client.get(f"/romancista/{novelist.id + 1}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"message": "Romancista não consta no MADR"}


def test_query_novelist_by_partial_name_success(client, novelist):
    partial_name = " assis"  # for 'machado de assis'
    response = client.get(f"romancista/?name={partial_name}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "romancistas": [{"nome": novelist.name, "id": novelist.id}]
    }


def test_query_novelists_by_partial_name_success(
    client, novelist, other_novelist
):
    partial_name = "ma"  # for 'machado' and 'maria'
    response = client.get(f"romancista/?name={partial_name}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "romancistas": [
            {"nome": novelist.name, "id": novelist.id},
            {"nome": other_novelist.name, "id": other_novelist.id},
        ]
    }


def test_query_novelists_no_matches_returns_empty_list(
    client, novelist, other_novelist
):
    name = "monteiro"
    response = client.get(f"romancista/?nome={name}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"romancistas": []}


def test_update_novelist_sucess(client, novelist, token):
    json_input = {"nome": "monteiro lobato"}
    response = client.patch(
        f"romancista/{novelist.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"nome": "monteiro lobato", "id": novelist.id}


def test_update_novelist_when_novelist_does_not_exist_not_found(
    client, novelist, token
):
    json_input = {"nome": "monteiro lobato"}
    response = client.patch(
        f"romancista/{novelist.id + 1}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"message": "Romancista não consta no MADR"}


def test_update_novelist_with_existing_novelist_name_conflict(
    client, novelist, other_novelist, token
):
    json_input = {"nome": other_novelist.name}
    response = client.patch(
        f"romancista/{novelist.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"message": "Romancista já consta no MADR"}


def test_update_novelist_with_own_novelist_name_success(
    client, novelist, token
):
    json_input = {"nome": novelist.name}
    response = client.patch(
        f"romancista/{novelist.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"nome": novelist.name, "id": novelist.id}


def test_update_novelist_not_authenticated_unauthorized(client, novelist):
    json_input = {"nome": novelist.name}
    response = client.patch(
        f"romancista/{novelist.id}",
        json=json_input,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_update_novelist_with_invalid_token_unauthorized(client, novelist):
    json_input = {"nome": novelist.name}
    response = client.patch(
        f"romancista/{novelist.id}",
        headers={"Authorization": "Bearer invalid token"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_delete_novelist_success(client, novelist, token):
    response = client.delete(
        f"romancista/{novelist.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Romancista deletado no MADR"}


def test_delete_novelist_not_authenticated_unauthorized(client, novelist):
    response = client.delete(
        f"romancista/{novelist.id}",
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_delete_novelist_with_invalid_token_unauthorized(client, novelist):
    response = client.delete(
        f"romancista/{novelist.id}",
        headers={"Authorization": "Bearer invalid token"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


@pytest.mark.asyncio
async def test_delete_novelist_also_deletes_their_books_success(
    session, client, novelist, other_novelist, token
):
    # register books by novelist
    books_novelist_quantity = 3
    books_novelist = BookFactory.create_batch(
        books_novelist_quantity, novelist_id=novelist.id
    )
    session.add_all(books_novelist)
    await session.commit()
    books_other_novelist_quantity = 2
    books_other_novelist = BookFactory.create_batch(
        books_other_novelist_quantity, novelist_id=other_novelist.id
    )
    session.add_all(books_other_novelist)
    await session.commit()
    # verify if all books as registered
    response = client.get("livro/?")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["livros"]) == (
        books_novelist_quantity + books_other_novelist_quantity
    )
    # verify if books exist
    response = client.get(f"livro/?romancista_id={novelist.id}")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["livros"]) == books_novelist_quantity
    # delete novelist
    response = client.delete(
        f"romancista/{novelist.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Romancista deletado no MADR"}
    # verify if books were deleted
    response = client.get(f"livro/?romancista_id={novelist.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"livros": []}
    # verify if books by other novelist
    response = client.get(f"livro/?romancista_id={other_novelist.id}")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["livros"]) == books_other_novelist_quantity


def test_novelist_name_sanitization_on_registry(client, token):
    name_unprocessed = "    novELIst    NaMe   "
    name_processed = "novelist name"
    json_input = {"nome": name_unprocessed}
    json_output = {"nome": name_processed, "id": 1}
    response = client.post(
        "romancista/",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == json_output


def test_novelist_name_sanitization_on_update(client, token, novelist):
    name_unprocessed = "    novELIst    NaMe   "
    name_processed = "novelist name"
    json_input = {"nome": name_unprocessed}
    json_output = {"nome": name_processed, "id": novelist.id}
    response = client.patch(
        f"romancista/{novelist.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output
