from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from mymadr.settings import settings

engine = create_async_engine(settings.DATABASE_URL)  # type: ignore


async def get_session():  # pragma: no cover
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
