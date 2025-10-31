from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mymadr.database import get_session
from mymadr.models import Account
from mymadr.schemas import Message, Token, User, UserOnUpdate, UserPublic
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


@router.post("/token", response_model=Token, tags=["auth"])
def login_for_access_token(form_data: TokenForm, session: GetSession):
    user = session.scalar(
        select(Account).where(Account.email == form_data.username)
    )
    if not user:  # email
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="USUARIO OU SENHA ERRADO",  # TODO arrumar mensagem
        )
    if not verify_password(form_data.password, user.password):  # senha
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="USUARIO OU SENHA ERRADO",  # TODO arrumar mensagem
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh-token", response_model=Token, tags=["auth"])
def refresh_access_token(current_user: GetCurrentUser):
    new_access_token = create_access_token(data={'sub': current_user.email})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/conta", response_model=UserPublic, tags=["user"])
def create_user(user: User, session: GetSession):
    db_user = session.scalar(
        select(Account).where(
            (Account.username == user.username) | (Account.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="USUARIO REPETIDO",  # TODO arrumar mensagem de erro
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="EMAIL REPETIDO",  # TODO arrumar mensagem de erro
            )
    hashed_password = get_password_hash(user.password.get_secret_value())
    user_info = Account(
        username=user.username, password=hashed_password, email=user.email
    )
    session.add(user_info)
    session.commit()
    session.refresh(user_info)
    return user_info


@router.put(
        "/conta/{user_id}",
        response_model=UserPublic,
        responses={HTTPStatus.FORBIDDEN: {"model": Message}},
        tags=["user"]
    )
def update_user(
    user_id: int,
    user: UserOnUpdate,
    session: GetSession,
    current_user: GetCurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            # TODO arruma a mensagem
            status_code=HTTPStatus.FORBIDDEN,
            detail="Não autorizado"
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
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            # TODO arruma mensagem
            detail="conflito de usuario ou email",
        )


@router.delete("/conta/{user_id}", response_model=Message, tags=["user"])
def delete_user(
    user_id: int,
    session: GetSession,
    current_user: GetCurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            # TODO arrumar a mensagem
            status_code=HTTPStatus.FORBIDDEN,
            detail="sem permissao",
        )
    session.delete(current_user)
    session.commit()
    # TODO arrumar mensagem
    return {"message": "usuario deletado com sucesso"}
