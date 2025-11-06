from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated, Optional
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, utils
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mymadr.database import get_session
from mymadr.models import Account
from mymadr.settings import Settings

settings = Settings()  # type: ignore


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(
        self, tokenUrl: str, custom_detail: str = "Not authenticated", **kwargs
    ):
        super().__init__(tokenUrl=tokenUrl, **kwargs)
        self.custom_detail = custom_detail

    async def __call__(self, request: Request):
        authorization: Optional[str] = request.headers.get("Authorization")
        scheme, _ = utils.get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail=self.custom_detail,
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return await super().__call__(request)


pwd_context = PasswordHash.recommended()
oauth2_scheme = CustomOAuth2PasswordBearer(
    tokenUrl="token",
    refreshUrl="token-refresh",
    auto_error=True,
    custom_detail="Não autorizado",
)
TokenForm = Annotated[str, Depends(oauth2_scheme)]
GetSession = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    session: GetSession,
    token: TokenForm,
):
    credential_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Não autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_email = payload.get("sub")
        if not subject_email:
            raise credential_exception
    except DecodeError:
        raise credential_exception
    user = await session.scalar(
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
