import os

import pytest
from fastapi.testclient import TestClient

# Point tests at the Docker-exposed Postgres (host port 5433)
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/secure_api_lab",
)

from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.db import models  # noqa: E402, F401 — register models
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    """Create all tables once per test session."""
    Base.metadata.create_all(bind=engine)
    yield


def _truncate():
    db = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _clean_tables():
    """Truncate all tables before and after each test for isolation."""
    _truncate()
    yield
    _truncate()


@pytest.fixture
def client() -> TestClient:
    """Provide a TestClient wired to the FastAPI app."""
    with TestClient(app) as c:
        yield c

