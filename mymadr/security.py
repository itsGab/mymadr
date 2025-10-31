from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from mymadr.database import get_session
from mymadr.models import Account
from mymadr.settings import settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='user/token', refreshUrl='user/token_refresh'
)
T_oauth2_scheme = Annotated[str, Depends(oauth2_scheme)]
T_session = Annotated[Session, Depends(get_session)]


def get_current_user(
    session: T_session,
    token: T_oauth2_scheme,
):
    credential_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='usuario nao validado',  # TODO arrumar mensagem
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_email = payload.get('sub')
        if not subject_email:
            raise credential_exception
    except DecodeError:
        raise credential_exception
    user = session.scalar(
        select(Account).where(Account.email == subject_email)
    )
    if not user:
        raise credential_exception
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = encode(
        payload=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
