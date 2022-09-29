import pytest
from fastapi.testclient import TestClient
from typing import Generator


from app.main import app
from app.db.session import SessionLocal


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
