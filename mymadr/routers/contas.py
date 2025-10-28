from fastapi import APIRouter

from mymadr.schemas import User, UserPublic

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", response_model=UserPublic)
def create_user(user: User):
    # FIXME create: create_user
    p_user = UserPublic(username=user.username, email=user.email, id=1)
    return p_user


@router.put("/")
def update_user():
    # TODO create: update user func
    ...


@router.delete("/")
def delete_user():
    # TODO create: delete user func
    ...
