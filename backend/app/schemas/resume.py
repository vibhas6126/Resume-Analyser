from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeRead(BaseModel):
    id: int
    original_filename: str
    content_type: str
    file_size_bytes: int
    page_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EducationItem(BaseModel):
    degree: str | None = None
    institution: str | None = None
    year: str | None = None
    raw_text: str


class ExperienceItem(BaseModel):
    title: str | None = None
    company: str | None = None
    date_range: str | None = None
    raw_text: str


class ProjectItem(BaseModel):
    name: str | None = None
    description: str
    technologies: list[str] = Field(default_factory=list)


class ParsedResume(BaseModel):
    skills: list[str] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)


class ResumeDetail(ResumeRead):
    extracted_text: str
    extracted_skills: list[str] | None = None
    extracted_education: list[EducationItem] | None = None
    extracted_experience: list[ExperienceItem] | None = None
    extracted_projects: list[ProjectItem] | None = None
    parsed_at: datetime | None = None


class ResumeParseResult(ResumeRead):
    parsed_at: datetime
    parsed_resume: ParsedResume


class ATSScoreResult(BaseModel):
    score: int
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    summary: str
