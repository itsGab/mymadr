from fastapi import APIRouter

router = APIRouter(prefix="/livro", tags=["livro"])


@router.post("/")
def register_book(): ...


@router.get("/")
def get_book(): ...


@router.get("/")
def get_books(): ...


@router.patch("/")
def update_book(): ...


@router.delete("/")
def delete_book(): ...
