from fastapi import APIRouter

router = APIRouter(prefix="/romancista", tags=["romancista"])


@router.post("/")
def register_romancista(): ...
