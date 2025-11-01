from fastapi import APIRouter

router = APIRouter(prefix="/livro", tags=["livro"])


@router.post("/")
def register_livro(): ...
