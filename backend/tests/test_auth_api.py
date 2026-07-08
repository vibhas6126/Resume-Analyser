import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.base import Base
from app.database.connection import get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_and_login_flow() -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "StrongPass123",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "ada@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ada@example.com",
            "password": "StrongPass123",
        },
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
