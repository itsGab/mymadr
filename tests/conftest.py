import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from mymadr.app import app
from mymadr.database import get_session
from mymadr.models import Account, Book, Novelist, table_registry
from mymadr.security import get_password_hash


@pytest_asyncio.fixture
async def client(session):
    async def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session):
    password = "password123"
    user = Account(
        username="usuario01",
        email="user1@mail.com",
        password=get_password_hash(password),  # type: ignore
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password  # type: ignore
    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = "password321"
    user = Account(
        username="usuario02",
        email="user2@mail.com",
        password=get_password_hash(password),  # type: ignore
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password  # type: ignore
    return user


@pytest_asyncio.fixture
async def token(client, user):
    response = client.post(
        "/token",
        data={
            "username": user.email,
            "password": user.clean_password,
        },
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def other_token(client, other_user):
    response = client.post(
        "/token",
        data={
            "username": other_user.email,
            "password": other_user.clean_password,
        },
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def novelist(session):
    novelist = Novelist(name="machado de assis")
    session.add(novelist)
    await session.commit()
    await session.refresh(novelist)
    return novelist


@pytest_asyncio.fixture
async def other_novelist(session):
    novelist = Novelist(name="maria firmina dos reis")
    session.add(novelist)
    await session.commit()
    await session.refresh(novelist)
    return novelist


@pytest_asyncio.fixture
async def book1(session, novelist):
    book = Book(
        title="dom casmurro",
        year=1899,
        novelist_id=novelist.id,
    )
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


@pytest_asyncio.fixture
async def book2(session, novelist):
    book = Book(
        title="missa do galo",
        year=1893,
        novelist_id=novelist.id,
    )
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


@pytest_asyncio.fixture
async def book3(session, other_novelist):
    book = Book(
        title="úrsula",
        year=1859,
        novelist_id=other_novelist.id,
    )
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book
