import re
from typing import Annotated, Optional

from pydantic import (
    AfterValidator,
    BaseModel,
    EmailStr,
    SecretStr,
)


def sanitizer(name: str) -> str:
    name = re.sub(r"\s+", " ", name.lower()).strip()
    return name


def username_sanitizer(username: str) -> str:
    return re.sub(r"[^\w]", "", username.lower())


SanitizedName = Annotated[  # sanitização dos nomes
    str, AfterValidator(sanitizer)
]

SanitizedUsername = Annotated[  # sanitização dos nomes de usuário
    str, AfterValidator(username_sanitizer)
]


class Message(BaseModel):
    message: str


class UserBasic(BaseModel):
    # todo: raise error?
    username: SanitizedUsername
    email: EmailStr


class UserSchema(UserBasic):
    password: SecretStr


class UserOnUpdate(BaseModel):
    username: Optional[SanitizedUsername] = None
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = None


class UserPublic(UserBasic):
    id: int


class Novelist(BaseModel):
    name: SanitizedName


class NovelistPublic(Novelist):
    id: int


class NovelistList(BaseModel):
    romancistas: list[NovelistPublic]


class Book(BaseModel):
    ano: int
    titulo: SanitizedName
    romancista_id: int


class BookPublic(Book):
    id: int


class BookList(BaseModel):
    livros: list[BookPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
