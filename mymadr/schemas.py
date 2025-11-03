import re
from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import HTTPException
from pydantic import (
    AfterValidator,
    BaseModel,
    EmailStr,
    SecretStr,
    model_validator,
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

    @model_validator(mode='after')
    def check_at_least_one_filed(cls, values):
        if not any([values.username, values.email, values.password]):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Pelo menos um campo deve ser fornecido"
            )
        return values


class UserPublic(UserBasic):
    id: int


class NovelistSchema(BaseModel):
    name: SanitizedName


class NovelistPublic(NovelistSchema):
    id: int


class NovelistList(BaseModel):
    romancistas: list[NovelistPublic]


class BookSchema(BaseModel):
    ano: int
    titulo: SanitizedName
    romancista_id: int


class BookPublic(BookSchema):
    id: int


class BookList(BaseModel):
    livros: list[BookPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
