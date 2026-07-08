from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.resume import (
    ATSScoreResult,
    ParsedResume,
    ResumeDetail,
    ResumeParseResult,
    ResumeRead,
)
from app.services.ats_service import ATSService
from app.services.resume_service import ResumeService
from app.utils.exceptions import (
    InvalidResumeFile,
    ResumeNotFound,
    ResumeParsingFailed,
)


router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post(
    "/upload",
    response_model=ResumeRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeRead:
    file_bytes = await file.read()

    try:
        return ResumeService.upload_resume(
            db=db,
            user=current_user,
            filename=file.filename or "",
            content_type=file.content_type or "",
            file_bytes=file_bytes,
        )
    except InvalidResumeFile as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ResumeParsingFailed as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[ResumeRead])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResumeRead]:
    return ResumeService.list_user_resumes(db=db, user=current_user)


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeDetail:
    try:
        return ResumeService.get_user_resume(
            db=db,
            user=current_user,
            resume_id=resume_id,
        )
    except ResumeNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{resume_id}/parse", response_model=ResumeParseResult)
def parse_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeParseResult:
    try:
        resume = ResumeService.parse_user_resume(
            db=db,
            user=current_user,
            resume_id=resume_id,
        )
    except ResumeNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ResumeParseResult(
        id=resume.id,
        original_filename=resume.original_filename,
        content_type=resume.content_type,
        file_size_bytes=resume.file_size_bytes,
        page_count=resume.page_count,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
        parsed_at=resume.parsed_at,
        parsed_resume=ParsedResume(
            skills=resume.extracted_skills or [],
            education=resume.extracted_education or [],
            experience=resume.extracted_experience or [],
            projects=resume.extracted_projects or [],
        ),
    )


@router.get("/{resume_id}/ats-score", response_model=ATSScoreResult)
def get_ats_score(
    resume_id: int,
    job_description: str = Query(..., min_length=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ATSScoreResult:
    try:
        resume = ResumeService.get_user_resume(
            db=db,
            user=current_user,
            resume_id=resume_id,
        )
    except ResumeNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ATSService.calculate_score(
        resume=resume,
        job_description=job_description,
    )
