from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mymadr.database import get_session
from mymadr.models import Account
from mymadr.schemas import Message, Token, UserOnUpdate, UserPublic, UserSchema
from mymadr.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter()

GetSession = Annotated[AsyncSession, Depends(get_session)]
TokenForm = Annotated[OAuth2PasswordRequestForm, Depends()]
GetCurrentUser = Annotated[Account, Depends(get_current_user)]


# --- conta ---
@router.post(
    "/conta",
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    responses={
        HTTPStatus.BAD_REQUEST: {"model": Message},
        HTTPStatus.CONFLICT: {"model": Message},
    },
    tags=["conta"],
)
async def create_user(user: UserSchema, session: GetSession):
    hashed_password = get_password_hash(user.password.get_secret_value())
    user_info = Account(
        username=user.username, password=hashed_password, email=user.email
    )
    try:
        session.add(user_info)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        er_msg = str(e.orig).lower()
        if "username" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Nome de usuário já consta no MADR",
            )
        if "email" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email já consta no MADR",
            )
        # trata qualquer IntegrityError inesperado
        raise HTTPException(  # pragma: no cover
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar usuário: ({er_msg})",
        )
    await session.refresh(user_info)
    return user_info


@router.put(
    "/conta/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={
        HTTPStatus.UNAUTHORIZED: {"model": Message},
        HTTPStatus.CONFLICT: {"model": Message},
        HTTPStatus.BAD_REQUEST: {"model": Message},
    },
    tags=["conta"],
)
async def update_user(
    user_id: int,
    user: UserOnUpdate,
    session: GetSession,
    current_user: GetCurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Não autorizado",
        )
    try:
        user_info = user.model_dump(exclude_unset=True)
        for field, value in user_info.items():
            if field == "password":
                hashed_password = get_password_hash(value.get_secret_value())
                setattr(current_user, field, hashed_password)
                continue
            setattr(current_user, field, value)
        await session.commit()
        await session.refresh(current_user)
        return current_user
    except IntegrityError as e:
        await session.rollback()
        er_msg = str(e.orig).lower()
        if "username" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=("Nome de usuário já consta no MADR"),
            )
        if "email" in er_msg:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=("Email já consta no MADR"),
            )
        # trata qualquer IntegrityError inesperado
        raise HTTPException(  # pragma: no cover
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar usuário: ({er_msg})",
        )


@router.delete(
    "/conta/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.UNAUTHORIZED: {"model": Message}},
    tags=["conta"],
)
async def delete_user(
    user_id: int,
    session: GetSession,
    current_user: GetCurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Não autorizado",
        )
    await session.delete(current_user)
    await session.commit()
    return {"message": "Conta deletada com sucesso"}


# --- auth ---
@router.post(
    "/token",
    response_model=Token,
    responses={HTTPStatus.BAD_REQUEST: {"model": Message}},
    tags=["auth"],
)
async def login_for_access_token(form_data: TokenForm, session: GetSession):
    user = await session.scalar(
        select(Account).where(Account.email == form_data.username)
    )
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Email ou senha incorretos",
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Email ou senha incorretos",
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh-token", response_model=Token, tags=["auth"])
def refresh_access_token(current_user: GetCurrentUser):
    new_access_token = create_access_token(data={"sub": current_user.email})
    return {"access_token": new_access_token, "token_type": "bearer"}
