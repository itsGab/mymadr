from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mymadr.models import Account, Author
from mymadr.schemas import (
    Message,
    NovelistFilter,
    NovelistList,
    NovelistPublic,
    NovelistSchema,
)
from mymadr.security import get_current_user, get_session

router = APIRouter(prefix="/romancista", tags=["romancista"])

GetSession = Annotated[Session, Depends(get_session)]
TokenForm = Annotated[OAuth2PasswordRequestForm, Depends()]
GetCurrentUser = Annotated[Account, Depends(get_current_user)]
QueryFilter = Annotated[NovelistFilter, Query()]


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=NovelistPublic,
    responses={},  # TODO adicionar os erros
)
def register_novelist(
    novelist: NovelistSchema,
    session: GetSession,
    current_user: GetCurrentUser,
):
    novelist_info = Author(novelist.name)
    try:
        session.add(novelist_info)
        session.commit()
        session.refresh(novelist_info)
        return novelist_info
    except IntegrityError as e:
        session.rollback()
        error_message = str(e.orig).lower()
        if "name" in error_message:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Romancista já consta no MADR",
            )
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Erro ao cadastrar romancista",
            )


@router.get(
    "/{novelist_id}",
    status_code=HTTPStatus.OK,
    response_model=NovelistPublic,
)
def get_novelist(novelist_id: int, session: GetSession):
    romancista_db = session.scalar(
        select(Author).where(Author.id == novelist_id)
    )
    if romancista_db:
        return romancista_db
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Romancista não consta no MADR",
        )


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=NovelistList,
)
def query_novelists(  # TODO paginar em 20
    session: GetSession,
    novelist_filter: QueryFilter,
):
    novelists_list = session.scalars(
        select(Author)
        .offset(novelist_filter.offset)
        .limit(novelist_filter.limit)
        .where(Author.name.contains(novelist_filter.name))
    )
    return {"romancistas": novelists_list.all()}


@router.patch(
    "/{novelist_id}",
    status_code=HTTPStatus.OK,
    response_model=NovelistPublic,
)
def update_novelist(
    novelist_id: int,
    novelist: NovelistSchema,
    session: GetSession,
    current_user: GetCurrentUser,
):
    try:
        novelist_db = session.scalar(
            select(Author).where(Author.id == novelist_id)
        )
        if not novelist_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Romancista não consta no MADR",
            )
        else:
            novelist_db.name = novelist.name
            session.commit()
            session.refresh(novelist_db)
            return novelist_db
    except IntegrityError as e:
        session.rollback()
        error_message = str(e.orig).lower()
        if "name" in error_message:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Romancista já consta no MADR",
            )
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Erro ao atualizar romancista",
            )


@router.delete(
    "/{novelist_id}",
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_novelist(
    novelist_id: int,
    session: GetSession,
    current_user: GetCurrentUser,
):
    try:
        novelist_db = session.scalar(
            select(Author).where(Author.id == novelist_id)
        )
        session.delete(novelist_db)
        session.commit()
        return {"message": "Romancista deletado no MADR"}
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Erro ao deletar romancista",
        )
