from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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

GetSession = Annotated[AsyncSession, Depends(get_session)]
GetCurrentUser = Annotated[Account, Depends(get_current_user)]
QueryFilter = Annotated[NovelistFilter, Query()]


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=NovelistPublic,
    responses={HTTPStatus.CONFLICT: {"model": Message}},
)
async def register_novelist(
    novelist: NovelistSchema,
    session: GetSession,
    current_user: GetCurrentUser,
):
    novelist_info = Novelist(novelist.name)
    try:
        session.add(novelist_info)
        await session.commit()
        await session.refresh(novelist_info)
        return novelist_info
    except IntegrityError as e:
        await session.rollback()
        er_msg = str(e.orig).lower()
        if "name" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Romancista já consta no MADR",
            )
        # trata qualquer IntegrityError inesperado
        raise HTTPException(  # pragma: no cover
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar romancista: ({er_msg})",
        )


@router.get(
    "/{novelist_id}",
    status_code=HTTPStatus.OK,
    response_model=NovelistPublic,
    responses={HTTPStatus.NOT_FOUND: {"model": Message}},
)
async def get_novelist(novelist_id: int, session: GetSession):
    romancista_db = await session.scalar(
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
async def query_novelists(
    session: GetSession,
    novelist_filter: QueryFilter,
):
    query = select(Novelist)
    if novelist_filter.name:
        query = query.filter(Novelist.name.contains(novelist_filter.name))
    novelists_list = await session.scalars(
        query.offset(novelist_filter.offset).limit(novelist_filter.limit)
    )
    return {"romancistas": novelists_list.all()}


@router.patch(
    "/{novelist_id}",
    status_code=HTTPStatus.OK,
    response_model=NovelistPublic,
    responses={
        HTTPStatus.NOT_FOUND: {"model": Message},
        HTTPStatus.CONFLICT: {"model": Message},
        HTTPStatus.BAD_REQUEST: {"model": Message},
    },
)
async def update_novelist(
    novelist_id: int,
    novelist: NovelistSchema,
    session: GetSession,
    current_user: GetCurrentUser,
):
    try:
        novelist_db = await session.scalar(
            select(Novelist).where(Novelist.id == novelist_id)
        )
        if not novelist_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Romancista não consta no MADR",
            )
        novelist_db.name = novelist.name
        await session.commit()
        await session.refresh(novelist_db)
        return novelist_db
    except IntegrityError as e:
        await session.rollback()
        er_msg = str(e.orig).lower()
        if "name" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Romancista já consta no MADR",
            )
        # trata qualquer IntegrityError inesperado
        raise HTTPException(  # pragma: no cover
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao atualizar romancista: ({er_msg})",
        )


@router.delete(
    "/{novelist_id}",
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.BAD_REQUEST: {"model": Message}},
)
async def delete_novelist(
    novelist_id: int,
    session: GetSession,
    current_user: GetCurrentUser,
):
    try:
        novelist_db = await session.scalar(
            select(Novelist).where(Novelist.id == novelist_id)
        )
        await session.delete(novelist_db)
        await session.commit()
        return {"message": "Romancista deletado no MADR"}
    # trata qualquer IntegrityError inesperado
    except IntegrityError:  # pragma: no cover
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Erro ao deletar romancista do MADR",
        )
