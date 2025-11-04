from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mymadr.database import get_session
from mymadr.models import Account, Novelist
from mymadr.schemas import (
    Message,
    NovelistFilter,
    NovelistList,
    NovelistPublic,
    NovelistSchema,
)
from mymadr.security import get_current_user

router = APIRouter(prefix="/romancista", tags=["romancista"])

GetSession = Annotated[Session, Depends(get_session)]
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
    novelist_info = Novelist(novelist.name)
    try:
        session.add(novelist_info)
        session.commit()
        session.refresh(novelist_info)
        return novelist_info
    except IntegrityError as e:
        session.rollback()
        er_msg = str(e.orig).lower()
        if "name" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Romancista já consta no MADR",
            )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar romancista: ({er_msg})",
        )


@router.get(
    "/{novelist_id}",
    status_code=HTTPStatus.OK,
    response_model=NovelistPublic,
)
def get_novelist(novelist_id: int, session: GetSession):
    romancista_db = session.scalar(
        select(Novelist).where(Novelist.id == novelist_id)
    )
    if romancista_db:
        return romancista_db
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail="Romancista não consta no MADR",
    )


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=NovelistList,
)
def query_novelists(
    session: GetSession,
    novelist_filter: QueryFilter,
):
    novelists_list = session.scalars(
        select(Novelist)
        .offset(novelist_filter.offset)
        .limit(novelist_filter.limit)
        .where(Novelist.name.contains(novelist_filter.name))
    )
    return {"livros": novelists_list.all()}


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
            select(Novelist).where(Novelist.id == novelist_id)
        )
        if not novelist_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Romancista não consta no MADR",
            )
        novelist_db.name = novelist.name
        session.commit()
        session.refresh(novelist_db)
        return novelist_db
    except IntegrityError as e:
        session.rollback()
        er_msg = str(e.orig).lower()
        if "name" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Romancista já consta no MADR",
            )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao atualizar romancista: ({er_msg})",
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
            select(Novelist).where(Novelist.id == novelist_id)
        )
        session.delete(novelist_db)
        session.commit()
        return {"message": "Romancista deletado no MADR"}
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Erro ao deletar romancista do MADR",
        )
