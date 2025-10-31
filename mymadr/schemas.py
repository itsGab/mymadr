from typing import Annotated

from pydantic import (
    BaseModel,
    EmailStr,
    PositiveInt,
    SecretStr,
    StringConstraints,
)

SanitizedStr = Annotated[  # para fazer sanitização dos nomes
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
    ),
]


class Message(BaseModel):
    message: str


class UserBasic(BaseModel):
    # TODO: faz sentido usar o sanitized aqui?
    # o username pode ter espaços, numero e simbolos?
    username: SanitizedStr
    email: EmailStr


class User(UserBasic):
    password: SecretStr


class UserPublic(UserBasic):
    id: int


class Romancista(BaseModel):
    name: SanitizedStr


class RomancistaPublic(Romancista):
    id: int


class RomancistaList(BaseModel):
    romancistas: list[UserPublic]


class Livro(BaseModel):
    ano: PositiveInt  # ano não pode ser negativo!
    titulo: SanitizedStr
    romancista_id: int


class LivroPublic(Livro):
    id: int


class LivroList(BaseModel):
    livros: list[LivroPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
