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


class UserPublic(UserBasic):
    id: int


# --- novelists ---
class NovelistSchema(BaseModel):
    name: SanitizedName


class NovelistPublic(NovelistSchema):
    id: int


class NovelistList(BaseModel):
    romancistas: list[NovelistPublic]


# --- books ---
class BookSchema(BaseModel):
    title: str
    year: int
    novelist_id: int


class BookOnUpdate(BaseModel):
    year: Optional[int] = None
    title: Optional[SanitizedName] = None
    novelist_id: Optional[int] = None

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
    livros: list[BookPublic]


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
    page_number: int = Field(1, ge=1, lt=50)
    _page_size: int = 20

    @property
    def limit(self) -> int:
        return self._page_size

    @property
    def offset(self) -> int:
        return (self.page_number - 1) * self._page_size


class NovelistFilter(FilterPage):
    name: SanitizedName | None = Field(min_length=1, max_length=20)


class BookFilter(FilterPagination):
    year: int | None = Field(None, le=date.today().year + 20)
    title: SanitizedName | None = Field(None, min_length=1, max_length=20)
    novelist_id: int | None = Field(None, gt=0)

    _valid_fields: bool = False  # check for at least one filled field

    @model_validator(mode="after")
    def check_valid_field(self) -> Self:
        if self._valid_fields:
            if not any([self.year, self.title, self.novelist_id]):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Pelo menos um campo deve ser fornecido",
                )
        return self
