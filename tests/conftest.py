import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from mymadr.app import app
from mymadr.database import get_session
from mymadr.models import Account, table_registry
from mymadr.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def user(session):
    password = "password123"
    user = Account(
        username="usuario01",
        email="user1@mail.com",
        password=get_password_hash(password),  # type: ignore
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    user.clean_password = password  # type: ignore
    return user


@pytest.fixture
def other_user(session):
    password = "password321"
    user = Account(
        username="usuario02",
        email="user2@mail.com",
        password=get_password_hash(password),  # type: ignore
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    user.clean_password = password  # type: ignore
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        "/token",
        data={
            "username": user.email,
            "password": user.clean_password,
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def other_token(client, other_user):
    response = client.post(
        "/token",
        data={
            "username": other_user.email,
            "password": other_user.clean_password,
        },
    )
    return response.json()["access_token"]
