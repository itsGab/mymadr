from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from mymadr.database import get_session
from mymadr.schemas import User, UserPublic
from mymadr.models import Account

router = APIRouter(prefix="/user", tags=["user"])

DbSession = Annotated[Session, Depends(get_session)]


@router.post("/", response_model=UserPublic)
def create_user(user: User, session: DbSession):
    # FIXME create: create_user
    db_user = Account(
        username=user.username, password=user.password, email=user.email
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.put("/")
def update_user():
    # TODO create: update user func
    ...


@router.delete("/")
def delete_user():
    # TODO create: delete user func
    ...
