import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.resume import Resume
from app.services.ats_service import ATSService


def test_calculate_ats_score() -> None:
    resume = Resume(
        id=1,
        user_id=1,
        original_filename="resume.pdf",
        stored_filename="resume.pdf",
        file_path="/tmp/resume.pdf",
        content_type="application/pdf",
        file_size_bytes=100,
        page_count=1,
        extracted_text="Python FastAPI React SQLAlchemy experience in backend systems.",
        extracted_skills=["Python", "FastAPI", "React", "SQLAlchemy"],
        extracted_education=[{"degree": "B.Tech", "institution": "Example University"}],
        extracted_experience=[{"title": "Backend Engineer", "company": "Acme"}],
        extracted_projects=[{"name": "ResumeIQ", "description": "Built AI resume analyzer"}],
        parsed_at=None,
    )

    result = ATSService.calculate_score(
        resume=resume,
        job_description="Backend engineer role focused on Python FastAPI React and SQLAlchemy.",
    )

    assert result.score >= 70
    assert "Python" in result.matched_skills
    assert "FastAPI" in result.matched_skills
    assert "React" in result.matched_skills
    assert "SQLAlchemy" in result.matched_skills
    assert result.missing_skills == []
