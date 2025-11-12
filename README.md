# Projeto Final do Incrível Curso de FastAPI

Ministrado por **Eduardo Mendes (Dunossauro)**

> 🎓 Link para o curso: [Curso Completo — FastAPI do Zero](https://fastapidozero.dunossauro.com/) <br>
> 📜 Proposta completa do projeto final: [Proposta de Projeto Final](https://fastapidozero.dunossauro.com/estavel/15/)

## Resumo da Proposta do Projeto Final

O desafio é construir uma API nos mesmos moldes da desenvolvida durante o curso, utilizando **FastAPI**, simulando um acervo digital de livros.

A aplicação se chama **MADR (Mader)** — *Meu Acervo Digital de Romances* — e gerencia **contas**, **romancistas** e **livros**.

Como essa é a minha abordagem do projeto ele se chama **myMADR**.

## Explicação das Escolhas

### Ferramentas Utilizadas

- **Python 3.14**
- **FastAPI**
- **SQLAlchemy**
- **Poetry** (`pyproject.toml` para gerenciamento de dependências)
- **PostgreSQL** (projeto migrado de SQLite para Postgres)
- **Docker** (containers para execução e banco de dados)
- **Pytest** (testes com **100% de cobertura**)

> Nos testes foi criado um **test_cenarios.py**, seguindo o exemplo do projeto final original.

## Estrutura de Rotas (Routers)

Conforme proposto, as rotas foram separadas da seguinte maneira

| Router      | Responsabilidade               | Endpoint(s)                          |
| ----------- | ------------------------------ | ------------------------------------ |
| `accounts`  | Gerencia contas e autenticação | `/conta`, `/token`, `/refresh-token` |
| `books`     | Gerencia livros                | `/livro`                             |
| `novelists` | Gerencia romancistas           | `/romancista`                        |

> Os nomes dos **routers e arquivos estão em inglês**, mas os **endpoints e tags estão em português**, mantendo consistência com o idioma da documentação.

### Conta (`/conta`)

Gerencia contas de usuário.  

- `POST`: **create_user** — cria uma nova conta de usuário  
- `PUT`: **update_user** — atualiza dados da conta existente  
- `DELETE`: **delete_user** — remove uma conta de usuário  

### Autorização (`/token`, `/refresh-token`)

Gerencia autenticação e renovação de tokens.  

- `POST /token`: **login_for_access_token** — gera um token JWT de autenticação por login
- `POST /refresh-token`: **refresh_access_token** — renova o token JWT se dentro da validade

### Livro (`/livro`)

Gerencia os recursos de livros.  

- `POST`: **register_book** — cria um novo livro  
- `GET /livro/{id}`: **get_book** — busca livro pelo ID  
- `GET /livro`: **query_books** — busca livros com filtros
- `PATCH /livro/{id}`: **update_book** — atualiza informações de um livro
- `DELETE /livro/{id}`: **delete_book** — remove um livro  

### Romancista (`/romancista`)

Gerencia autores (romancistas) cadastrados.  

- `POST`: **register_novelist** — cria um novo romancista  
- `GET /romancista/{id}`: **get_novelist** — busca romancista pelo ID  
- `GET /romancista`: **query_novelists** — busca romancistas com filtros
- `PATCH /romancista/{id}`: **update_novelist** — atualiza dados de um romancista  
- `DELETE /romancista/{id}`: **delete_novelist** — remove um romancista  

## Schemas e Tipagem

Os tipos e validacoes baseados no material do curso, com algumas alterações como:

- Validação e sanitização
  - Validação e sanitização de **strings** (nomes, títulos e `username`) utilizando tipos `Annotated` e `AfterValidator`.
  - Nomes e títulos têm **espaços desnecessários removidos** automaticamente.
  - `username` é normalizado para **letras minúsculas**, **sem espaços** e **sem caracteres especiais**.
- Value e type checking com Pydantic
  - Uso de `Field()` para definição de **valores padrão**, **alias** (traduções para exibição) e **metadados de schema**.
  - Schemas de **atualização (update)** aceitam campos vazios, mas exigem **ao menos um campo preenchido**.
- Paginação
  - Criado modelo `FilterPagination` com limite fixo de **20 itens por página**, e parâmetro `page` (padrão: `1`).

### Exemplo de validação e sanitização

O projeto utiliza **tipos anotados (`Annotated`)** com **`AfterValidator()`** para sanitização e validação dos campos.
Foram criados tipos personalizados para **nomes**, **títulos** e **nomes de usuário**, com funções validadoras específicas.

```python
# --- funções de sanitização ---
def str_sanitizer(name: str) -> str:
    name = re.sub(r"\s+", " ", name.strip())
    return name

def user_sanitizer(username: str) -> str:
    return re.sub(r"[^\w]", "", username.strip().lower())

# --- tipo sanitizado ---
SanitizedString = Annotated[str, AfterValidator(str_sanitizer)]
SanitizedUsername = Annotated[str, AfterValidator(user_sanitizer)]
```

### Exemplo de value e type checking com Pydantic

Os schemas de entrada utilizam o `Field()` para configurar metadados, exemplos e aliases, além de validadores customizados via `@model_validator`. No exemplo abaixo, o schema de atualização de usuário exige que pelo menos um campo seja informado.

``` python
# --- modelo de entrada de atualizacao de conta ---
class UserOnUpdate(BaseModel):
    # campos opcionais com validação e alias
    username: Optional[SanitizedUsername] = Field(
        None, examples=["nome_de_usuario"]
    )
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = Field(
        None, alias="senha", examples=["senha"]
    )

    # aceita entradas com `aliases`
    model_config = ConfigDict(populate_by_name=True)

    # valida se pelo menos um campo e informado
    @model_validator(mode="after")
    def check_valid_field(self) -> Self:
        if not any([self.username, self.email, self.password]):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ResponseMessage.DATA_MISSING_FIELDS,
            )
        return self
```

### Exemplo de paginação

O modelo de paginação (`FilterPagination`) define os parâmetros padrão de busca paginada, com limite fixo de 20 itens por página. A propriedade `offset` é calculada automaticamente a partir da página solicitada. O modelo `BookFilter` estende essa estrutura, permitindo filtragem por campos opcionais, com validação de conteúdo.

``` python
# --- modelo de paginacao ---
class FilterPagination(BaseModel):
    # numero da pagina e quantidade itens por pagina
    page: int = Field(1, ge=1, lt=50, alias="pagina")
    page_size: int = Field(20, frozen=True)

    # calcula e define `limit` e `offset`
    @property
    def limit(self) -> int:
        return self.page_size
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

# filtro de paginacao para livros
class BookFilter(FilterPagination):
    # campos aceitos para filtragem
    year: int | None = Field(None, le=date.today().year + 20, alias="ano")
    title: SanitizedString | None = Field(
        None, min_length=1, max_length=20, alias="titulo"
    )
    novelist_id: int | None = Field(None, gt=0, alias="romancista_id")

    # aceita entradas com `aliases`
    model_config = ConfigDict(populate_by_name=True)

    # valida se pelo menos um campo foi fornecido (opcional)
    _valid_fields: bool = False
    @model_validator(mode="after")
    def check_valid_field(self) -> Self:
        if self._valid_fields:
            if not any([self.year, self.title, self.novelist_id]):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=ResponseMessage.DATA_MISSING_FIELDS,
                )
        return self
```

## Tratamento de Exceções e Mensagens

### Use de `exception_handler` personalizado

Foi criado um **manipulador de exceções** que ajusta o formato de saída dos erros para se alinhar ao formato esperado no projeto final.

### Implementação

```python
@app.exception_handler(HTTPException)
def message_http_exception_handler(request: Request, exc: HTTPException):
    """Substitui 'detail' por 'message' nas respostas de erro."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
        headers=getattr(exc, "headers", None),
    )
```

Resultado

```json
{"message": "Mensagem"}
```

em vez de

```json
{"detail": "Mensagem"}
```

### Criação do módulo `messages.py`

Foi criado um módulo **`messages.py`** para centralizar mensagens e textos de erro, inspirado no `HTTPStatus`.

```python
from enum import Enum

class ResponseMessage(str, Enum):
    # account / auth
    ACCOUNT_USERNAME_CONFLICT = "Nome de usuário já consta no MADR"
    ACCOUNT_EMAIL_CONFLICT = "Email já consta no MADR"
    ACCOUNT_DELETED_SUCCESS = "Conta deletada com sucesso"
    AUTH_INVALID_CREDENTIALS = "Email ou senha incorretos"
    AUTH_NOT_AUTHORIZED = "Não autorizado"

    # book
    BOOK_NOT_FOUND = "Livro não consta no MADR"
    BOOK_DELETED_SUCCESS = "Livro deletado no MADR"

    # novelist
    NOVELIST_CONFLICT = "Romancista já consta no MADR"
    NOVELIST_NOT_FOUND = "Romancista não consta no MADR"
    NOVELIST_DELETED_SUCCESS = "Romancista deletado no MADR"

    # data validation
    DATA_MISSING_FIELDS = "Pelo menos um campo deve ser fornecido"
```

### Personalização de Mensagem de Erro de Autenticação

Foi implementado um **`CustomOAuth2PasswordBearer`** sobre o **`OAuth2PasswordBearer`** para ajustar a mensagem de autenticação padrão.

- Substituído por **"Não autenticado"**, o retorno segue o formato esperado pelo projeto final:

``` json
{"message": "Não autenticado"}
```

> Fora essa alteração de texto, o comportamento padrão do `OAuth2PasswordBearer` foi mantido.

### Captura de Erros de Integridade

Em alguns endpoints foi incluído **tratamento de `IntegrityError`**, garantindo respostas mais seguras e controladas em casos de violação de integridade no banco de dados. Não foi testado, pois não consegui fazer chegar nesse erro, tipo um Fail Check.

## Cobertura de Testes

Os testes estão organizados por domínio da aplicação para facilitar a manutenção e o entendimento.  
Cada arquivo cobre uma parte do sistema (contas, livros, romancistas, segurança, etc.) usando o pytest.

- **`conftest.py`**: traz fixtures globais que são usadas nos testes, como o cliente da aplicação, configuração do banco de teste e criação de usuários.  
- **`factories.py`**: tem funções para criar dados de exemplo, livros, para facilitar os testes.  
- **Testes por domínio**: arquivos como `test_accounts.py`, `test_books.py`, `test_novelists.py` e `test_security.py` testam cada parte da aplicação.  
- **Cenários integrados**: o arquivo `test_cenarios.py` junta testes que simulam fluxos reais, seguindo o que foi pedido na proposta do projeto.  
- **Test Containers**: os testes rodam usando containers com banco Postgres, garantindo que o ambiente seja o mais parecido possível com o real.

Os testes são isolados, focam em usar dados controlados e nomes claros, e podem ser executados com

> p.s.: esqueci de cobrir o test de tempo de validacao do token

## Como Executar o Projeto (com Docker Compose)

### 1️. Clonar o repositório

``` bash
git clone https://github.com/itsGab/mymadr.git
cd mymadr
```

ou

``` bash
gh repo clone itsGab/mymadr
cd mymadr
```

### 2. Executar com Docker

```bash
docker compose up --build
```

## Considerações Finais

O **mymadr** é a entrega do projeto final do curso FastAPI do Zero e fiquei bastante satisfeito com o resultado. A API atende a todas as propostas iniciais, gerenciando contas, autenticação, romancistas e livros, oferecendo um CRUD completo.

Além do que foi solicitado, gostei da forma como abordei alguns temas, como a *validação e sanitização de dados*, e também explorei assuntos que não foram abordados diretamente no curso, mas que decidi incluir, como o módulo `message.py` com o `ResponseModel` (inspirado no `HTTPStatus`).

O *tratamento de erros* foi outro ponto interessante, sendo adaptado ao `schema` do `Message`. Isso permitiu substituir respostas genéricas, como o `detail`, por um formato consistente: por exemplo, erros de autorização agora retornam `{"message": "Não autorizado"}` em vez da mensagem padrão do `CustomOAuth2PasswordBearer`.

A implementação da *paginação* também seguiu o proposto, configurando um tamanho fixo de página de 20 registros, mas com uma abordagem um pouco diferente do apresentado no curso. A integração da *paginação com os filtros (query)*, conforme ensinada no curso, trouxe uma solução eficiente e prática para o projeto.

**Só tenho a agradecer pelo material: foi muito enriquecedor estudar, replicar, praticar e concluir este projeto.**
