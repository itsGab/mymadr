from http import HTTPStatus

import pytest

from tests.factories import BookFactory


def test_register_book_success(client, novelist, token):
    json_input = {
        "titulo": "memórias póstumas de brás cubas",
        "ano": 1880,
        "romancista_id": novelist.id,
    }
    json_output = {
        "titulo": "memórias póstumas de brás cubas",
        "ano": 1880,
        "romancista_id": novelist.id,
        "id": 1,
    }
    response = client.post(
        "livro",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == json_output


def test_register_book_when_novelist_does_not_exist_not_found(client, token):
    json_input = {
        "titulo": "memórias póstumas de brás cubas",
        "ano": 1880,
        "romancista_id": "1",
    }
    response = client.post(
        "livro",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"message": "Romancista não consta no MADR"}


def test_get_book_by_id_success(client, book1):
    response = client.get(f"livro/{book1.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "titulo": book1.title,
        "ano": book1.year,
        "romancista_id": book1.novelist_id,
        "id": book1.id,
    }


def test_get_book_by_id_when_book_does_not_exist_not_found(client, book1):
    response = client.get(f"livro/{book1.id + 1}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"message": "Livro não consta no MADR"}


def test_query_book_by_partial_title_success(client, book1, book2, book3):
    partial_name = "dom cas"  # dom casmurro
    response = client.get(f"livro/?pagina=1&titulo={partial_name}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "livros": [
            {
                "titulo": book1.title,
                "ano": book1.year,
                "romancista_id": book1.novelist_id,
                "id": book1.id,
            }
        ]
    }


def test_query_book_by_year_success(client, book1, book2, book3):
    response = client.get(f"livro/?ano={book1.year}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "livros": [
            {
                "titulo": book1.title,
                "ano": book1.year,
                "romancista_id": book1.novelist_id,
                "id": book1.id,
            }
        ]
    }


def test_query_book_by_novelist_id_success(client, book1, book2, book3):
    response = client.get(f"livro/?romancista_id={book1.novelist_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "livros": [
            {
                "titulo": book1.title,
                "ano": book1.year,
                "romancista_id": book1.novelist_id,
                "id": book1.id,
            },
            {
                "titulo": book2.title,
                "ano": book2.year,
                "romancista_id": book2.novelist_id,
                "id": book2.id,
            },
        ]
    }


def test_query_book_by_no_matches_return_empty_list(client, book1):
    partial_name = "úrsula"  # dom casmurro
    response = client.get(f"livro/?titulo={partial_name}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"livros": []}


def test_update_book_title_success(client, book1, token):
    new_title = "novo titulo"
    json_output = {
        "titulo": new_title,
        "ano": book1.year,
        "romancista_id": book1.novelist_id,
        "id": book1.id,
    }
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"titulo": new_title},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_update_book_when_book_does_not_exist_not_found(client, book1, token):
    new_title = "novo titulo"
    response = client.patch(
        f"livro/{book1.id + 1}",
        headers={"Authorization": f"Bearer {token}"},
        json={"titulo": new_title},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"message": "Livro não consta no MADR"}


def test_update_book_with_all_fields_provided_success(
    client, book1, other_novelist, token
):
    new_title = "novo titulo"
    new_year = 2025
    new_novelist_id = other_novelist.id
    json_output = {
        "titulo": new_title,
        "ano": new_year,
        "romancista_id": new_novelist_id,
        "id": book1.id,
    }
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "titulo": new_title,
            "ano": new_year,
            "romancista_id": new_novelist_id,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_update_book_with_no_fields_provided_bad_request(client, book1, token):
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        "message": "Pelo menos um campo deve ser fornecido"
    }


def test_update_book_year_success(client, book1, token):
    new_year = 2025
    json_output = {
        "titulo": book1.title,
        "ano": new_year,
        "romancista_id": book1.novelist_id,
        "id": book1.id,
    }
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"ano": new_year},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_update_book_novelist_id_success(client, book1, other_novelist, token):
    new_novelist_id = other_novelist.id
    json_output = {
        "titulo": book1.title,
        "ano": book1.year,
        "romancista_id": new_novelist_id,
        "id": book1.id,
    }
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"romancista_id": new_novelist_id},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_update_book_novelist_id_when_novelist_does_not_exist_not_found(
    client, book1, token
):
    new_novelist_id = 2
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"romancista_id": new_novelist_id},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"message": "Romancista não consta no MADR"}


def test_update_book_with_existing_title_success(client, book1, book2, token):
    json_output = {
        "titulo": book2.title,
        "ano": book1.year,
        "romancista_id": book1.novelist_id,
        "id": book1.id,
    }
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"titulo": book2.title},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == json_output


def test_update_book_not_authenticated_unauthorized(client, book1):
    new_title = "novo titulo"
    response = client.patch(
        f"livro/{book1.id}",
        json={"titulo": new_title},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_update_book_invalid_token_unauthorized(client, book1):
    new_title = "novo titulo"
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": "Bearer invalid token"},
        json={"titulo": new_title},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_delete_book_success(client, book1, token):
    response = client.delete(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Livro deletado no MADR"}


def test_delete_book_not_authenticated_unauthorized(client, book1):
    response = client.delete(
        f"livro/{book1.id}",
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


def test_delete_book_invalid_token_unauthorized(client, book1):
    response = client.delete(
        f"livro/{book1.id}",
        headers={"Authorization": "Bearer invalid token"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"message": "Não autorizado"}


@pytest.mark.asyncio
async def test_book_pagination_size_first_page_returns_20_of_30_books(
    session, client, novelist
):
    """test pagination (max size 20 books per page):
    has 30 books
    expects 20 of 30 books in response
    """
    books_quantity = 30
    default_page_size = 20
    len_expected = default_page_size
    session.add_all(
        BookFactory.create_batch(books_quantity, novelist_id=novelist.id)
    )
    await session.commit()
    response = client.get("livro/?")  # <- page not provided
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["livros"]) == len_expected


@pytest.mark.asyncio
async def test_book_pagination_size_second_page_returns_10_of_30_books(
    session, client, novelist
):
    """test pagination - 2nd page (max size 20 books per page):
    has 30 books
    expects 10 of 30 books in response
    """
    books_quantity = 30
    default_page_size = 20
    page = 2
    len_expected = books_quantity - default_page_size
    session.add_all(BookFactory.create_batch(books_quantity))
    await session.commit()
    response = client.get(f"livro/?pagina={page}")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["livros"]) == len_expected


def test_book_title_sanitization_on_registry(client, token, novelist):
    title_unprocessed = "  tHE  Title     "
    title_processed = "the title"
    json_input = {
        "titulo": title_unprocessed,
        "ano": 2025,
        "romancista_id": novelist.id,
    }
    json_output = {
        "titulo": title_processed,
        "ano": 2025,
        "romancista_id": novelist.id,
        "id": 1,
    }
    response = client.post(
        "livro", headers={"Authorization": f"Bearer {token}"}, json=json_input
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == json_output


def test_book_title_sanitization_on_update(client, book1, token, novelist):
    title_unprocessed = "  tHE  Title     "
    title_processed = "the title"
    json_input = {"titulo": title_unprocessed}
    json_output = {
        "titulo": title_processed,
        "ano": book1.year,
        "romancista_id": novelist.id,
        "id": book1.id,
    }
    response = client.patch(
        f"livro/{book1.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=json_input,
    )
    assert response.json() == json_output
    assert response.status_code == HTTPStatus.OK
