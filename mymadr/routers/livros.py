from fastapi import APIRouter

router = APIRouter(prefix='/livros', tags=['livros'])


@router.post('/')
def register_livro():
    ...
