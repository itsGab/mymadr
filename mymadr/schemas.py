from pydantic import BaseModel, EmailStr


class UserBasic(BaseModel):
    username: str
    email: EmailStr


class User(UserBasic):
    password: str


class UserPublic(UserBasic):
    id: int


class Romancista(BaseModel):
    name: str


class RomancistaPublic(Romancista):
    id: int


class RomancistaList(BaseModel):
    romancistas: list[UserPublic]


class Livro(BaseModel):
    # TODO: validacao no Ano do livro.
    ano: int  # ??? Field(..., ge=0)
    titulo: str
    romancista_id: int


class LivroPublic(Livro):
    id: int


class LivroList(BaseModel):
    livros: list[LivroPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
