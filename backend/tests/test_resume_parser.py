import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.base import Base
from app.models.resume import Resume
from app.models.user import User
from app.services.resume_service import ResumeService


def test_resume_parsing_flow() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)

    user = User(
        full_name="Ada Lovelace",
        email="parser@example.com",
        hashed_password="hash",
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    resume = Resume(
        user_id=user.id,
        original_filename="resume.pdf",
        stored_filename="resume.pdf",
        file_path="/tmp/resume.pdf",
        content_type="application/pdf",
        file_size_bytes=100,
        page_count=1,
        extracted_text="""
Education
B.Tech in Computer Science
University of Example 2024

Experience
Software Engineer at Acme 2022-2024

Projects
ResumeIQ Platform
Built FastAPI services using Python and React
""".strip(),
    )
    session.add(resume)
    session.commit()
    session.refresh(resume)

    parsed_resume = ResumeService.parse_user_resume(
        db=session,
        user=user,
        resume_id=resume.id,
    )

    assert parsed_resume.extracted_skills == ["FastAPI", "Python", "React"]
    assert parsed_resume.extracted_education[0]["degree"] == "B.Tech"
    assert parsed_resume.extracted_experience[0]["title"] == "Software Engineer"
    assert parsed_resume.extracted_projects[0]["name"] == "ResumeIQ Platform"
    assert parsed_resume.parsed_at is not None
