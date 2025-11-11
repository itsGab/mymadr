from http import HTTPStatus


# Funcionalidade: Gerenciamento de conta
def test_criacao_de_conta(client):
    # Cenário: Criação de conta
    """
    Quando enviar um "POST" em "/user"
    """
    input = {
        "username": "dunossauro",
        "email": "dudu@dudu.com",
        "password": "123456",
    }
    """
    Então devo receber o status "201"
    E o json contendo
    """
    status = HTTPStatus.CREATED
    output = {"email": "dudu@dudu.com", "username": "dunossauro", "id": 1}

    response = client.post("/conta", json=input)

    assert response.status_code == status
    assert response.json() == output


def test_alteracao_de_conta(client):
    # Cenário: Alteração de conta
    """
    Quando enviar um "POST" em "/user"
    """
    input = {
        "username": "dunossauro",
        "email": "dudu@dudu.com",
        "password": "123456",
    }
    """
    Quando enviar um "PUT" em "/user/1"
    """
    update = {
        "username": "dunossauro",
        "email": "dudu@dudu.com",
        "password": "654321",
    }
    client.post("/conta", json=input)
    response = client.post(
        "token", data={"username": "dudu@dudu.com", "password": "123456"}
    )
    token = response.json()["access_token"]
    response = client.put(
        "/conta/1", headers={"Authorization": f"Bearer {token}"}, json=update
    )
    """
    Então devo receber o status "200"
    E o json contendo
    """
    status = HTTPStatus.OK
    output = {"username": "dunossauro", "email": "dudu@dudu.com", "id": 1}
    assert response.json() == output
    assert response.status_code == status


def test_delecao_da_conta(client, token):
    # Cenário: Deleção da conta
    """
    Quando enviar um "POST" em "/user"
    """
    input = {
        "username": "dunossauro",
        "email": "dudu@dudu.com",
        "password": "123456",
    }
    """
    Quando enviar um "DELETE" em "/user/1"
    Então devo receber o status "200"
    E o json contendo
    """
    status = HTTPStatus.OK
    output = {"message": "Conta deletada com sucesso"}
    client.post("conta", json=input)
    response = client.delete(
        "conta/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status
    assert response.json() == output


def test_criacao_de_conta_ja_existente(client):
    # Cenário: Criação de conta já existente
    """
    Quando enviar um "POST" em "/user"
    """
    input = {
        "username": "dunossauro",
        "email": "dudu@dudu.com",
        "password": "123456",
    }
    """
    Quando enviar um "POST" em "/user"
    """
    input2 = {
        "username": "dunossauro",
        "email": "dudu@dudu.com",
        "password": "123456",
    }
    """
    Então devo receber o status "400"
    E o json contendo
    """
    status = HTTPStatus.CONFLICT
    # output = {"detail": "Conta já cadastrada"} <- TODO: anotar arrumar!!!
    output = {"message": "Nome de usuário já consta no MADR"}
    client.post("conta", json=input)
    response = client.post("conta", json=input2)
    assert response.status_code == status
    assert response.json() == output


def test_autenticacao_via_jwt(client):
    # Cenário: Autenticação via JWT
    """
    Quando enviar um "POST" em "/token"
    """
    input = {
        "username": "fausto",
        "email": "fausto@fausto.com",
        "password": "12345",
    }
    input_data = {"username": "fausto@fausto.com", "password": "12345"}
    """
    Então devo receber o status "200"
    E o json contendo

    # modelo de token esperado (exemplo)
    output = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
        eyJzdWIiOiJ0ZXN0ZUB0ZXN0LmNvbSIsImV4cCI6MTY5MDI1ODE1M30.
        Nx0P_ornVwJBH_LLLVrlJoh6RmJeXR-Nr7YJ_mlGY04",
        "token_type": "bearer"
    }
    """
    status = HTTPStatus.OK
    client.post("conta", json=input)
    response = client.post("token", data=input_data)
    assert response.status_code == status
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_autenticacao_via_jwt_com_usuario_nao_existente(client):
    # Cenário: Autenticação via JWT com usuário não existente
    """
    Quando enviar um "POST" em "/token"
    """
    input_data = {"username": "fausto@fausto.com", "password": "12345"}
    """
    Então devo receber o status "400"
    E o json contendo
    """
    status = HTTPStatus.BAD_REQUEST
    output = {"message": "Email ou senha incorretos"}
    response = client.post("token", data=input_data)
    assert response.status_code == status
    assert response.json() == output


def test_autorizacao_via_bearer_token(client):
    # Cenário: Autorização via Bearer token
    """
    Dado que envie um "POST" em "/token"
    """
    input = {
        "username": "fausto",
        "email": "fausto@fausto.com",
        "password": "12345",
    }
    input_data = {"username": "fausto@fausto.com", "password": "12345"}
    # TODO: anotar arrumar !!!
    """                         /romancista <- correto
    Quando enviar um "POST" em "/livro"
    """
    input_livro = {"nome": "Clarice Lispector"}
    """
    Então deve receber o status "201"
    E o json contendo
    """
    status = HTTPStatus.CREATED
    # TODO: arrumar !!!
    # output = {"id": 42, "nome": "Clarice Lispector"} <- arrumar p/ minusculo
    output = {"id": 1, "nome": "clarice lispector"}
    client.post("conta", json=input)
    response = client.post("token", data=input_data)
    token = response.json()["access_token"]
    response = client.post(
        "romancista",
        headers={"Authorization": f"Bearer {token}"},
        json=input_livro,
    )
    assert response.status_code == status
    assert response.json() == output


def test_tentativa_de_operacao_sem_autorizacao(client):
    # TODO: arrumar !!!!
    # Cenário: Tentativa de operação sem autorização
    """ "/romancista" <- correto
    Quando enviar um "POST" em "/livro" <- errado
    """
    input = {"nome": "Clarice Lispector"}
    """
    Então deve receber o status "401"
    E o json contendo
    """
    status = HTTPStatus.UNAUTHORIZED
    output = {"message": "Não autorizado"}
    response = client.post(
        "romancista",
        headers={"Authorization": "Bearer invalid-token"},
        json=input,
    )
    assert response.status_code == status
    assert response.json() == output


# Funcionalidade: Gerenciamente de livro


def test_registro_de_livro(client, token, novelist):
    # Cenário: Registro de livro
    """
    Quando enviar um "POST" em "/livro/"
    """
    input = {
        "ano": 1973,
        "titulo": "Café Da Manhã Dos Campeões",
        "romancista_id": 1,
    }
    """
    Então devo receber o status "201"
    E o json contendo
    """
    status = HTTPStatus.CREATED
    output = {
        "ano": 1973,
        "titulo": "café da manhã dos campeões",
        "romancista_id": 1,
        "id": 1,  # TODO: arrumar <- esperado um id
    }
    response = client.post(
        "livro", headers={"Authorization": f"Bearer {token}"}, json=input
    )
    assert response.status_code == status
    assert response.json() == output


def test_alteracao_de_livro(client, token, novelist):
    # Cenário: Alteração de livro
    """
    Quando enviar um "PATCH" em "/livro/1"
    """
    input = {
        "ano": 1973,
        "titulo": "Café Da Manhã Dos Campeões",
        "romancista_id": 1,
    }
    input_update = {"ano": 1974}
    """

    Então devo receber o status "200"
    E o json contendo
    """
    status = HTTPStatus.OK
    output = {
        "ano": 1974,
        "titulo": "café da manhã dos campeões",
        "romancista_id": 1,
        "id": 1,  # TODO: arrumar <- esperado um id
    }
    client.post(
        "livro", headers={"Authorization": f"Bearer {token}"}, json=input
    )
    response = client.patch(
        "livro/1",
        headers={"Authorization": f"Bearer {token}"},
        json=input_update,
    )
    assert response.status_code == status
    assert response.json() == output


def test_buscar_livro_por_id(client, token, novelist):
    # Cenário: Buscar livro por ID
    """Quando enviar um "GET" em "/livro/1"
    Então devo receber o status "200"
    E o json contendo
    """
    input = {
        "ano": 1974,
        "titulo": "Café Da Manhã Dos Campeões",
        "romancista_id": 1,
    }
    status = HTTPStatus.OK
    output = {
        "ano": 1974,
        "titulo": "café da manhã dos campeões",
        "romancista_id": 1,
        "id": 1,  # TODO: arrumar <- esperado um id
    }
    client.post(
        "livro", headers={"Authorization": f"Bearer {token}"}, json=input
    )
    response = client.get("livro/1")
    assert response.status_code == status
    assert response.json() == output


def test_delecao_de_livro(client, token, novelist):
    # Cenário: Deleção de livro
    """Quando enviar um "DELETE" em "/livro/1"

    Então devo receber o status "200"
    E o json contendo
    """
    input = {
        "ano": 1973,
        "titulo": "Café Da Manhã Dos Campeões",
        "romancista_id": 1,
    }
    status = HTTPStatus.OK
    output = {"message": "Livro deletado do MADR"}
    client.post(
        "livro", headers={"Authorization": f"Bearer {token}"}, json=input
    )
    response = client.delete(
        "livro/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status
    assert response.json() == output


def test_filtro_de_livros(client, token, novelist, other_novelist):
    # Cenário: Filtro de livros
    """
    Quando enviar um "POST" em "/livro/"
    """
    input1 = {
        "ano": 1900,
        "titulo": "Café Da Manhã Dos Campeões",
        "romancista_id": 1,
    }
    """
    E enviar um "POST" em "/livro/"
    """
    input2 = {
        "ano": 1900,
        "titulo": "Memórias Póstumas de Brás Cubas",
        "romancista_id": 2,
    }
    """
    E enviar um "POST" em "/livro/"
    """
    input3 = {"ano": 1865, "titulo": "Iracema", "romancista_id": 2}
    """
    E enviar um "GET" em "/livro/?titulo=a&ano=1900"

    Então devo receber o status "200"
    E o json contendo
    """
    status = HTTPStatus.OK
    output = {
        "livros": [
            {
                "ano": 1900,
                "titulo": "café da manhã dos campeões",
                "romancista_id": 1,
                "id": 1,
            },
            {
                "ano": 1900,
                "titulo": "memórias póstumas de brás cubas",
                "romancista_id": 2,
                "id": 2,
            },
        ]
    }
    client.post(
        "livro", headers={"Authorization": f"Bearer {token}"}, json=input1
    )
    client.post(
        "livro", headers={"Authorization": f"Bearer {token}"}, json=input2
    )
    client.post(
        "livro", headers={"Authorization": f"Bearer {token}"}, json=input3
    )
    response = client.get("livro/?titulo=a&ano=1900")
    assert response.status_code == status
    assert response.json() == output


# Funcionalidade: Romancistas


def test_criacao_de_romancista(client, token):
    # Cenário: Criação de Romancista
    """
    Quando enviar um "POST" em "/romancista"
    """
    input = {"nome": "Clarice Lispector"}
    """
    Então devo receber o status "201"
    E o json contendo
    """
    status = HTTPStatus.CREATED
    output = {"nome": "clarice lispector", "id": 1}
    response = client.post(
        "romancista", headers={"Authorization": f"Bearer {token}"}, json=input
    )
    assert response.status_code == status
    assert response.json() == output


def test_buscar_romancista_por_id(client, token):
    # Cenário: Buscar romancista por ID
    """
    Quando enviar um "GET" em "/romancista/1"
    Então devo receber o status "200"
    E o json contendo
    """
    input = {"nome": "Clarice Lispector"}
    status = HTTPStatus.OK
    output = {"nome": "clarice lispector", "id": 1}
    client.post(
        "romancista", headers={"Authorization": f"Bearer {token}"}, json=input
    )
    response = client.get("romancista/1")
    assert response.status_code == status
    assert response.json() == output


def test_alteracao_de_romancista(client, token):
    # Cenário: Alteração de Romancista
    """
    Quando enviar um "PUT" em "/romancista/1"
    """
    input = {"nome": "Clarice Lispector"}
    input_update = {"nome": "manuel bandeira"}
    """
    Então devo receber o status "200"
    E o json contendo
    """
    status = HTTPStatus.OK
    output = {
        "nome": "manuel bandeira",
        "id": 1,  # <- nao tem id na saida TODO: arrumar
    }
    client.post(
        "romancista", headers={"Authorization": f"Bearer {token}"}, json=input
    )
    response = client.patch(
        "romancista/1",
        headers={"Authorization": f"Bearer {token}"},
        json=input_update,
    )
    assert response.status_code == status
    assert response.json() == output


def test_delecao_de_romancista(client, token):
    # Cenário: Deleção de Romancista
    """
    Quando enviar um "DELETE" em "/romancista/1"
    Então devo receber o status "200"
    E o json contendo
    """
    input = {"nome": "Clarice Lispector"}
    status = HTTPStatus.OK
    output = {"message": "Romancista deletado no MADR"}
    client.post(
        "romancista", headers={"Authorization": f"Bearer {token}"}, json=input
    )
    response = client.delete(
        "romancista/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status
    assert response.json() == output


def test_buscar_de_romancistas_por_filtro(client, token):
    # Cenário: Busca de romancistas por filtro
    """
    Quando enviar um "POST" em "/romancista"
    """
    input1 = {"nome": "Clarice Lispector"}
    """

    E enviar um "POST" em "/romancista"
    """
    input2 = {"nome": "Manuel Bandeira"}
    """

    E enviar um "POST" em "/romancista"
    """
    input3 = {"nome": "Paulo Leminski"}
    """
    Quando enviar um "GET" em "/romancista?nome=a"
    Então devo receber o status "200"
    E o json contendo
    """
    status = HTTPStatus.OK
    output = {
        "romancistas": [
            {"nome": "clarice lispector", "id": 1},
            {"nome": "manuel bandeira", "id": 2},
            {"nome": "paulo leminski", "id": 3},
        ]
    }
    client.post(
        "romancista", headers={"Authorization": f"Bearer {token}"}, json=input1
    )
    client.post(
        "romancista", headers={"Authorization": f"Bearer {token}"}, json=input2
    )
    client.post(
        "romancista", headers={"Authorization": f"Bearer {token}"}, json=input3
    )
    response = client.get("romancista?nome=a")
    assert response.status_code == status
    assert response.json() == output
