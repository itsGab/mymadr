from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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

GetSession = Annotated[Session, Depends(get_session)]
TokenForm = Annotated[OAuth2PasswordRequestForm, Depends()]
GetCurrentUser = Annotated[Account, Depends(get_current_user)]


@router.post(
    "/token",
    response_model=Token,
    responses={HTTPStatus.BAD_REQUEST: {"model": Message}},
    tags=["auth"],
)
def login_for_access_token(form_data: TokenForm, session: GetSession):
    user = session.scalar(
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


@router.post(
    "/conta",
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    responses={HTTPStatus.CONFLICT: {"model": Message}},
    tags=["user"],
)
def create_user(user: UserSchema, session: GetSession):
    hashed_password = get_password_hash(user.password.get_secret_value())
    user_info = Account(
        username=user.username, password=hashed_password, email=user.email
    )
    try:
        session.add(user_info)
        session.commit()
        session.refresh(user_info)
        return user_info
    except IntegrityError as e:
        session.rollback()
        er_msg = str(e.orig).lower()
        conflict_src = None
        if "username" in er_msg:
            conflict_src = "Nome de usuário"
        elif "email" in er_msg:
            conflict_src = "Email"
        if conflict_src:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=(f"{conflict_src} já consta no MADR"),
            )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar usuário: ({er_msg})",
        )


@router.put(
    "/conta/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={
        HTTPStatus.UNAUTHORIZED: {"model": Message},
        HTTPStatus.CONFLICT: {"model": Message},
    },
    tags=["user"],
)
def update_user(
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
        if user.username:
            current_user.username = user.username
        if user.email:
            current_user.email = user.email
        if user.password:
            hashed = get_password_hash(user.password.get_secret_value())
            current_user.password = hashed
        session.commit()
        session.refresh(current_user)
        return current_user
    except IntegrityError as e:
        session.rollback()
        er_msg = str(e.orig).lower()
        conflict_src = None
        if "username" in er_msg:
            conflict_src = "Nome de usuário"
        elif "email" in er_msg:
            conflict_src = "Email"
        if conflict_src:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=(f"{conflict_src} já consta no MADR"),
            )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Erro de integridade ao cadastrar usuário: ({er_msg})",
        )


@router.delete(
    "/conta/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.UNAUTHORIZED: {"model": Message}},
    tags=["user"],
)
def delete_user(
    user_id: int,
    session: GetSession,
    current_user: GetCurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Não autorizado",
        )
    session.delete(current_user)
    session.commit()
    return {"message": "Conta deletada com sucesso"}
