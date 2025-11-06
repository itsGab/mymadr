from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mymadr.settings import settings

engine = create_engine(settings.DATABASE_URL)  # type: ignore


def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session
