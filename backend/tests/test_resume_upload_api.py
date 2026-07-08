import io
import sys
import tempfile
from pathlib import Path

import fitz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
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


def test_resume_upload_flow() -> None:
    temp_dir = Path(tempfile.mkdtemp())
    settings.upload_dir = temp_dir

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Ada Lovelace",
            "email": "resume-upload@example.com",
            "password": "StrongPass123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "resume-upload@example.com",
            "password": "StrongPass123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Python FastAPI SQLAlchemy Resume")
    pdf_bytes = document.tobytes()
    document.close()

    upload_response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert upload_response.status_code == 201
    payload = upload_response.json()
    assert payload["original_filename"] == "resume.pdf"
    assert payload["page_count"] == 1
