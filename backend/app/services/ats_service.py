from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.resume import Resume


@dataclass(frozen=True)
class ATSScoreResult:
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    summary: str


class ATSService:
    """Calculate a lightweight ATS compatibility score for a resume."""

    @staticmethod
    def calculate_score(resume: Resume, job_description: str) -> ATSScoreResult:
        extracted_skills = [skill.lower() for skill in (resume.extracted_skills or [])]
        job_terms = [term.lower() for term in ATSService._tokenize(job_description)]

        matched_skills = [
            skill for skill in (resume.extracted_skills or [])
            if ATSService._skill_matches(skill.lower(), job_terms)
        ]

        job_skills = ATSService._extract_job_skills(job_description)
        job_skill_names = [skill.lower() for skill in job_skills]
        missing_skills = [
            skill for skill in job_skills
            if skill.lower() not in extracted_skills
        ]
        if not missing_skills and not job_skill_names:
            missing_skills = []

        if not matched_skills:
            score = 40
        else:
            score = min(100, 40 + (len(matched_skills) * 15))

        summary = (
            f"Resume matched {len(matched_skills)} of the requested skills."
        )
        return ATSScoreResult(
            score=score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            summary=summary,
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token for token in text.replace("/", " ").split() if token]

    @staticmethod
    def _skill_matches(skill: str, job_terms: list[str]) -> bool:
        return any(skill == term or skill in term or term in skill for term in job_terms)

    @staticmethod
    def _extract_job_skills(job_description: str) -> list[str]:
        normalized = job_description.lower()
        supported_skills = [
            ("python", "Python"),
            ("fastapi", "FastAPI"),
            ("react", "React"),
            ("sqlalchemy", "SQLAlchemy"),
            ("docker", "Docker"),
            ("aws", "AWS"),
            ("azure", "Azure"),
            ("machine learning", "Machine Learning"),
            ("ai", "AI"),
            ("sql", "SQL"),
        ]

        matched_skills = []
        for alias, display_name in supported_skills:
            pattern = rf"(?<![a-z0-9+#.]){re.escape(alias)}(?![a-z0-9+#.])"
            if re.search(pattern, normalized):
                matched_skills.append(display_name)

        return matched_skills
