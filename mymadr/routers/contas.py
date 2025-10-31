from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from mymadr.database import get_session
from mymadr.models import Account
from mymadr.schemas import Token, User, UserPublic
from mymadr.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/user", tags=["user"])

DbSession = Annotated[Session, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token/", response_model=Token,)
def login_for_access_token(form_data: OAuth2Form, session: DbSession):
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


@router.post("/token/refresh/", response_model=Token)
def refresh_token(): ...


@router.post("/", response_model=UserPublic)
def create_user(user: User, session: DbSession):
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
    hashed_password = get_password_hash(user.password)
    user_info = Account(
        username=user.username, password=hashed_password, email=user.email
    )
    session.add(user_info)
    session.commit()
    session.refresh(user_info)
    return user_info


@router.put("/")
def update_user():
    # TODO create: update user func
    ...


@router.delete("/")
def delete_user():
    # TODO create: delete user func
    ...
