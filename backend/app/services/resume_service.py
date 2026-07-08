from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.resume import Resume
from app.models.user import User
from app.parser.pdf_parser import PdfParser
from app.parser.resume_parser import ResumeParser
from app.utils.exceptions import (
    InvalidResumeFile,
    ResumeNotFound,
    ResumeParsingFailed,
)


class ResumeService:
    """Use cases for resume upload, parsing, and retrieval."""

    allowed_content_types = {"application/pdf"}

    @staticmethod
    def upload_resume(
        db: Session,
        user: User,
        filename: str,
        content_type: str,
        file_bytes: bytes,
    ) -> Resume:
        ResumeService._validate_pdf_upload(
            filename=filename,
            content_type=content_type,
            file_size=len(file_bytes),
        )

        parsed_pdf = PdfParser.extract_text(file_bytes)
        stored_path = ResumeService._store_file(
            user_id=user.id,
            original_filename=filename,
            file_bytes=file_bytes,
        )

        resume = Resume(
            user_id=user.id,
            original_filename=filename,
            stored_filename=stored_path.name,
            file_path=str(stored_path),
            content_type=content_type,
            file_size_bytes=len(file_bytes),
            page_count=parsed_pdf.page_count,
            extracted_text=parsed_pdf.text,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def list_user_resumes(db: Session, user: User) -> list[Resume]:
        statement = (
            select(Resume)
            .where(Resume.user_id == user.id)
            .order_by(Resume.created_at.desc())
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def get_user_resume(db: Session, user: User, resume_id: int) -> Resume:
        statement = select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user.id,
        )
        resume = db.scalar(statement)
        if resume is None:
            raise ResumeNotFound("Resume not found.")
        return resume

    @staticmethod
    def parse_user_resume(db: Session, user: User, resume_id: int) -> Resume:
        resume = ResumeService.get_user_resume(
            db=db,
            user=user,
            resume_id=resume_id,
        )
        parsed_resume = ResumeParser.parse(resume.extracted_text)

        resume.extracted_skills = parsed_resume.skills
        resume.extracted_education = [
            item.model_dump(exclude_none=True) for item in parsed_resume.education
        ]
        resume.extracted_experience = [
            item.model_dump(exclude_none=True) for item in parsed_resume.experience
        ]
        resume.extracted_projects = [
            item.model_dump(exclude_none=True) for item in parsed_resume.projects
        ]
        resume.parsed_at = parsed_resume.parsed_at

        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def _validate_pdf_upload(
        filename: str,
        content_type: str,
        file_size: int,
    ) -> None:
        if not filename.lower().endswith(".pdf"):
            raise InvalidResumeFile("Only PDF resumes are supported.")

        if content_type not in ResumeService.allowed_content_types:
            raise InvalidResumeFile("Uploaded file must be a PDF.")

        if file_size == 0:
            raise InvalidResumeFile("Uploaded file is empty.")

        if file_size > settings.max_upload_size_bytes:
            raise InvalidResumeFile(
                f"PDF size must be {settings.max_upload_size_mb} MB or less.",
            )

    @staticmethod
    def _store_file(
        user_id: int,
        original_filename: str,
        file_bytes: bytes,
    ) -> Path:
        safe_suffix = Path(original_filename).suffix.lower()
        stored_filename = f"{uuid4().hex}{safe_suffix}"
        user_upload_dir = settings.upload_dir / f"user_{user_id}"
        user_upload_dir.mkdir(parents=True, exist_ok=True)

        stored_path = user_upload_dir / stored_filename
        try:
            stored_path.write_bytes(file_bytes)
        except OSError as exc:
            raise ResumeParsingFailed("Unable to store the uploaded resume.") from exc

        return stored_path
