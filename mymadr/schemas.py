import re
from datetime import date
from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import HTTPException
from pydantic import (
    AfterValidator,
    BaseModel,
    EmailStr,
    Field,
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


class FilterPage(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)


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


class NovelistFilter(FilterPage):
    name: SanitizedName | None = Field(min_length=1, max_length=20)


class BookSchema(BaseModel):
    ano: int
    titulo: SanitizedName
    romancista_id: int


class BookPublic(BookSchema):
    id: int


class BookList(BaseModel):
    livros: list[BookPublic]


class BookFilter(FilterPage):
    # ano é menor que ano atual + 20 anos
    ano: int | None = Field(None, le=date.today().year + 20)
    titulo: SanitizedName | None = Field(None, min_length=3, max_length=20)
    romancista_id: int | None = Field(None, gt=0)


class Token(BaseModel):
    access_token: str
    token_type: str
