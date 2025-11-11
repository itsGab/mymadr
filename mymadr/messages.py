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
