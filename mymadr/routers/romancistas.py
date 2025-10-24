from fastapi import APIRouter


router = APIRouter(prefix='/romancistas', tags=['romancistas'])

@router.post('/')
def register_romancista():
    ...