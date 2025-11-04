from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mymadr.database import get_session
from mymadr.models import Account, Book, Novelist
from mymadr.schemas import (
    BookFilter,
    BookList,
    BookOnUpdate,
    BookPublic,
    BookSchema,
    Message,
)
from mymadr.security import get_current_user

router = APIRouter(prefix="/livro", tags=["livro"])

GetSession = Annotated[Session, Depends(get_session)]
GetCurrentUser = Annotated[Account, Depends(get_current_user)]
QueryFilter = Annotated[BookFilter, Query()]


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=BookPublic,
)
def register_book(
    book: BookSchema,
    session: GetSession,
    # current_user: GetCurrentUser,
):
    novelist = session.scalar(
        select(Novelist).where(Novelist.id == book.novelist_id)
    )
    if not novelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Romancista não consta no MADR",
        )
    book_info = Book(
        title=book.title, year=book.year, novelist_id=book.novelist_id
    )
    try:
        session.add(book_info)
        session.commit()
        session.refresh(book_info)
        return book_info
    except IntegrityError as er:
        session.rollback()
        er_msg = str(er.orig).lower()
        if "novelist_id" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Romancista não consta no MADR",
            )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar livro: ({er_msg})",
        )


@router.get("/{book_id}", status_code=HTTPStatus.OK, response_model=BookPublic)
def get_book(book_id: int, session: GetSession):
    book_db = session.scalar(select(Book).where(Book.id == book_id))
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Livro não consta no MADR",
        )
    return book_db


@router.get(
    "/query/",
    status_code=HTTPStatus.OK,
    response_model=BookList,
    responses={HTTPStatus.BAD_REQUEST: {"model": Message}},
)
def query_books(session: GetSession, book_filter: QueryFilter):
    query = select(Book)
    if book_filter.title:
        query = query.filter(Book.title.contains(book_filter.title))
    if book_filter.year:
        query = query.filter(Book.year == book_filter.year)
    if book_filter.novelist_id:
        query = query.filter(Book.novelist_id == book_filter.novelist_id)
    books_list = session.scalars(
        query.offset(book_filter.offset).limit(book_filter.limit)
    )
    return {"livros": books_list.all()}


@router.patch("/{book_id}", status_code=HTTPStatus.OK)
def update_book(
    book_id: int,
    book: BookOnUpdate,
    session: GetSession,
    # current_user: GetCurrentUser
):
    # return book.model_dump(exclude_unset=True)
    book_db = session.scalar(select(Book).where(Book.id == book_id))
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Livro não consta no MADR",
        )
    try:
        book_info = book.model_dump(exclude_unset=True)
        for field, value in book_info.items():
            setattr(book_db, field, value)
        # if book.title:
        #     book_db.title = book.title
        # if book.year:
        #     book_db.year = book.year
        # if book.novelist_id:
        #     book_db.novelist_id = book.novelist_id
        session.commit()
        session.refresh(book_db)
        return book_db
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="algo deu ruim",  # TODO arrumar erro
        )


@router.delete(
    "/{book_id}",
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_book(
    book_id: int,
    session: GetSession,
    # current_user: GetCurrentUser,
):
    try:
        book_db = session.scalar(select(Book).where(Book.id == book_id))
        session.delete(book_db)
        session.commit()
        return {"message": "Livro deletado do MADR"}
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Erro ao deletar livro do MADR",
        )
