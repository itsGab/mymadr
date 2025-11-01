import re
from typing import Annotated, Optional

from pydantic import (
    AfterValidator,
    BaseModel,
    EmailStr,
    PositiveInt,
    SecretStr,
)


def sanitizer(name: str) -> str:
    name = re.sub(r"\s+", " ", name.lower()).strip()
    return name


SanitizedStr = Annotated[  # para fazer sanitização dos nomes
    str, AfterValidator(sanitizer)
]


class Message(BaseModel):
    message: str


class UserBasic(BaseModel):
    # TODO: faz sentido usar o sanitized aqui?
    # o username pode ter espaços, numero e simbolos?
    username: SanitizedStr
    email: EmailStr


class UserSchema(UserBasic):
    password: SecretStr


class UserOnUpdate(BaseModel):
    username: Optional[SanitizedStr] = None
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = None


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
