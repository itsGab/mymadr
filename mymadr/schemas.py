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

    @model_validator(mode="after")
    def check_at_least_one_filed(cls, values):
        if not any([values.username, values.email, values.password]):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Pelo menos um campo deve ser fornecido",
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
    year: int
    title: SanitizedName
    novelist_id: int


class BookPublic(BookSchema):
    id: int


class BookList(BaseModel):
    livros: list[BookPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, gt=0, le=100, description="Tamanho da página")

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class NovelistFilter(FilterPage):
    name: SanitizedName | None = Field(min_length=1, max_length=20)


class BookFilter(FilterPage):
    # ano tem que ser menor que ano atual + 20 anos
    year: int | None = Field(None, le=date.today().year + 20)
    title: SanitizedName | None = Field(None, min_length=3, max_length=20)
    novelist_id: int | None = Field(None, gt=0)
