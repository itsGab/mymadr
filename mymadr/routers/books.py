from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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

GetSession = Annotated[AsyncSession, Depends(get_session)]
GetCurrentUser = Annotated[Account, Depends(get_current_user)]
QueryFilter = Annotated[BookFilter, Query()]


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=BookPublic,
    responses={
        HTTPStatus.NOT_FOUND: {"model": Message},
        HTTPStatus.BAD_REQUEST: {"model": Message},
    },
)
async def register_book(
    book: BookSchema,
    session: GetSession,
    current_user: GetCurrentUser,
):
    novelist = await session.scalar(
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
        await session.commit()
        await session.refresh(book_info)
        return book_info
    except IntegrityError as er:  # pragma: no cover
        """FIXME a checagem no novelist.id pra ver se existe esta acontecendo
        no comeco da funcao, por aqui nao funciona. eu nao sei se eh por causa
        do sqlite, lembre de testar novamente quando migrar para postgres"""

        await session.rollback()
        er_msg = str(er.orig).lower()
        if "novelist_id" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Romancista não consta no MADR",
            )
        # trata qualquer IntegrityError inesperado
        raise HTTPException(  # pragma: no cover
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar livro: ({er_msg})",
        )


@router.get(
    "/{book_id}",
    status_code=HTTPStatus.OK,
    response_model=BookPublic,
    responses={HTTPStatus.NOT_FOUND: {"model": Message}},
)
async def get_book(book_id: int, session: GetSession):
    book_db = await session.scalar(select(Book).where(Book.id == book_id))
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Livro não consta no MADR",
        )
    return book_db


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=BookList,
)
async def query_books(session: GetSession, book_filter: QueryFilter):
    query = select(Book)
    if book_filter.title:
        query = query.filter(Book.title.contains(book_filter.title))
    if book_filter.year:
        query = query.filter(Book.year == book_filter.year)
    if book_filter.novelist_id:
        query = query.filter(Book.novelist_id == book_filter.novelist_id)
    books_list = await session.scalars(
        query.offset(book_filter.offset).limit(book_filter.limit)
    )
    return {"livros": books_list.all()}


@router.patch(
    "/{book_id}",
    status_code=HTTPStatus.OK,
    response_model=BookPublic,
    responses={
        HTTPStatus.NOT_FOUND: {"model": Message},
        HTTPStatus.CONFLICT: {"model": Message},
    },
)
async def update_book(
    book_id: int,
    book: BookOnUpdate,
    session: GetSession,
    current_user: GetCurrentUser,
):
    book_db = await session.scalar(select(Book).where(Book.id == book_id))
    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Livro não consta no MADR",
        )
    if book.novelist_id is not None:
        romancista_db = await session.scalar(
            select(Novelist).where(Novelist.id == book.novelist_id)
        )
        if not romancista_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Romancista não consta no MADR",
            )
    try:
        book_info = book.model_dump(exclude_unset=True)
        for field, value in book_info.items():
            setattr(book_db, field, value)
        await session.commit()
        await session.refresh(book_db)
        return book_db
    except IntegrityError as e:  # pragma: no cover
        await session.rollback()
        er_msg = str(e.orig).lower()
        # trata qualquer IntegrityError inesperado
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Erro de integridade ao atualizar livro: ({er_msg})",
        )


@router.delete(
    "/{book_id}",
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.BAD_REQUEST: {"model": Message}},
)
async def delete_book(
    book_id: int,
    session: GetSession,
    current_user: GetCurrentUser,
):
    try:
        book_db = await session.scalar(select(Book).where(Book.id == book_id))
        await session.delete(book_db)
        await session.commit()
        return {"message": "Livro deletado do MADR"}
    except IntegrityError:  # pragma: no cover
        await session.rollback()
        # trata qualquer IntegrityError inesperado
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Erro ao deletar livro do MADR",
        )
