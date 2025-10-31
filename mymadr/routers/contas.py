from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mymadr.database import get_session
from mymadr.models import Account
from mymadr.schemas import Message, Token, User, UserPublic
from mymadr.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/user")

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


@router.post("/token_refresh", response_model=Token, tags=["auth"])
def refresh_token(): ...  # TODO fazer o refresh


@router.post("/", response_model=UserPublic, tags=["user"])
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


@router.put("/{user_id}", response_model=UserPublic, tags=["user"])
def update_user(
    # TODO create: update user func
    user_id: int,
    user: User,
    session: GetSession,
    current_user: GetCurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            # TODO arruma a mensagem
            status_code=HTTPStatus.FORBIDDEN,
            detail="nao tem permissao",
        )
    try:
        hashed = get_password_hash(user.password.get_secret_value())
        current_user.username = user.username
        current_user.password = hashed
        current_user.email = user.email
        session.commit()
        session.refresh(current_user)
        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            # TODO arruma mensagem
            detail="conflito de usuario ou email",
        )


@router.delete("/{user_id}", response_model=Message, tags=["user"])
def delete_user(
    user_id: int,
    session: GetSession,
    current_user: GetCurrentUser,
):
    # TODO create: delete user func
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
