import re
from datetime import date
from http import HTTPStatus
from typing import Annotated, Optional, Self

from fastapi import HTTPException
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    model_validator,
)


# --- funções de sanitização e annotated ---
def str_sanitizer(name: str) -> str:
    name = re.sub(r"\s+", " ", name.lower()).strip()
    return name


def user_sanitizer(username: str) -> str:
    return re.sub(r"[^\w]", "", username.lower())


SanitizedString = Annotated[  # sanitização dos nomes
    str, AfterValidator(str_sanitizer)
]

SanitizedUsername = Annotated[  # sanitização dos nomes de usuário
    str, AfterValidator(user_sanitizer)
]


# --- message ---
class Message(BaseModel):
    message: str


# --- accounts ---
class UserBasic(BaseModel):
    username: SanitizedUsername = Field(examples=["nome_de_usuario"])
    email: EmailStr

    model_config = ConfigDict(populate_by_name=True)


class UserSchema(UserBasic):
    password: SecretStr = Field(..., alias="senha", examples=["senha"])


class UserPublic(UserBasic):
    id: int


class UserOnUpdate(BaseModel):
    username: Optional[SanitizedUsername] = Field(
        None, examples=["nome_de_usuario"]
    )
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = Field(
        None, alias="senha", examples=["senha"]
    )

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def check_valid_field(self) -> Self:
        if not any([self.username, self.email, self.password]):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Pelo menos um campo deve ser fornecido",
            )
        return self


# --- novelists ---
class NovelistSchema(BaseModel):
    name: SanitizedString = Field(alias="nome")

    model_config = ConfigDict(populate_by_name=True)


class NovelistPublic(NovelistSchema):
    id: int


class NovelistList(BaseModel):
    novelists: list[NovelistPublic] = Field(alias="romancistas")


# --- books ---
class BookSchema(BaseModel):
    title: SanitizedString = Field(alias="titulo")
    year: int = Field(alias="ano")
    novelist_id: int = Field(alias="romancista_id")

    model_config = ConfigDict(populate_by_name=True)


class BookOnUpdate(BaseModel):
    title: Optional[SanitizedString] = Field(None, alias="titulo")
    year: Optional[int] = Field(None, alias="ano")
    novelist_id: Optional[int] = Field(None, alias="romancista_id")

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def check_valid_field(self) -> Self:
        if not any([self.year, self.title, self.novelist_id]):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Pelo menos um campo deve ser fornecido",
            )
        return self


class BookPublic(BookSchema):
    id: int


class BookList(BaseModel):
    books: list[BookPublic] = Field(alias="livros")


# --- auth ---
class Token(BaseModel):
    access_token: str
    token_type: str


# --- filters ---
# BY OFFSET AND LIMIT
class FilterPage(BaseModel):
    offset: int = Field(0, ge=0, lt=980)
    limit: int = Field(20, ge=1, lt=100)


# BY PAGES OF 20
class FilterPagination(BaseModel):
    page: int = Field(1, ge=1, lt=50, alias="pagina")
    _page_size: int = 20

    @property
    def limit(self) -> int:
        return self._page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self._page_size


class NovelistFilter(FilterPagination):
    name: Optional[SanitizedString] = Field(
        None, min_length=1, max_length=50, alias="nome"
    )

    model_config = ConfigDict(populate_by_name=True)


class BookFilter(FilterPagination):
    year: int | None = Field(None, le=date.today().year + 20, alias="ano")
    title: SanitizedString | None = Field(
        None, min_length=1, max_length=20, alias="titulo"
    )
    novelist_id: int | None = Field(None, gt=0, alias="romancista_id")

    model_config = ConfigDict(populate_by_name=True)

    # when True checks for at least one filled field
    _valid_fields: bool = False

    @model_validator(mode="after")  # pragma: no cover
    def check_valid_field(self) -> Self:
        if self._valid_fields:
            if not any([self.year, self.title, self.novelist_id]):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Pelo menos um campo deve ser fornecido",
                )
        return self
