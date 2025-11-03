from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mymadr.database import get_session
from mymadr.models import Account, Book
from mymadr.schemas import BookPublic, BookSchema
from mymadr.security import get_current_user

router = APIRouter(prefix="/livro", tags=["livro"])

GetSession = Annotated[Session, Depends(get_session)]
GetCurrentUser = Annotated[Account, Depends(get_current_user)]
QueryFilter = ...


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=BookPublic,
)
def register_book(
    book: BookSchema,
    session: GetSession,
    current_user: GetCurrentUser,
):
    book_info = Book(
        title=book.title, year=book.year, author_id=book.novelist_id
    )
    try:
        session.add(book_info)
        session.commit()
        session.refresh(book_info)
        return book_info
    except IntegrityError as er:
        session.rollback()
        er_msg = str(er.orig).lower()
        if 'author_id' in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Romancista não consta no MADR"
            )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar livro: ({er_msg})"
        )


@router.get("/")
def get_book(): ...


@router.get("/")
def query_books(): ...


@router.patch("/")
def update_book(): ...


@router.delete("/")
def delete_book(): ...
