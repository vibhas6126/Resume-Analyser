import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.parser.skill_taxonomy import SKILL_KEYWORDS
from app.schemas.resume import EducationItem, ExperienceItem, ProjectItem


SECTION_ALIASES = {
    "education": "education",
    "academic background": "education",
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment history": "experience",
    "projects": "projects",
    "personal projects": "projects",
    "academic projects": "projects",
    "skills": "skills",
    "technical skills": "skills",
    "technologies": "skills",
}

SECTION_NAMES = "|".join(re.escape(section) for section in SECTION_ALIASES)
SECTION_PATTERN = re.compile(
    rf"^\s*({SECTION_NAMES})\s*:?\s*$",
    re.IGNORECASE,
)
DATE_RANGE_PATTERN = re.compile(
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?\.?\s*"
    r"\d{4})\s*(?:-|to|–)\s*((?:present|current)|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)?\.?\s*\d{4})",
    re.IGNORECASE,
)
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
DEGREE_PATTERN = re.compile(
    r"\b(B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?|BSc|MSc|BCA|MCA|MBA|Bachelor|Master|PhD|Diploma)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedResumeData:
    skills: list[str] = field(default_factory=list)
    education: list[EducationItem] = field(default_factory=list)
    experience: list[ExperienceItem] = field(default_factory=list)
    projects: list[ProjectItem] = field(default_factory=list)
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ResumeParser:
    """Extract structured resume data from normalized resume text."""

    @staticmethod
    def parse(text: str) -> ParsedResumeData:
        normalized_text = ResumeParser._normalize_text(text)
        sections = ResumeParser._split_sections(normalized_text)
        skills = ResumeParser._extract_skills(normalized_text)

        return ParsedResumeData(
            skills=skills,
            education=ResumeParser._extract_education(sections.get("education", "")),
            experience=ResumeParser._extract_experience(
                sections.get("experience", ""),
            ),
            projects=ResumeParser._extract_projects(
                sections.get("projects", ""),
                skills,
            ),
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = [line.strip() for line in text.replace("\r", "\n").split("\n")]
        return "\n".join(line for line in lines if line)

    @staticmethod
    def _split_sections(text: str) -> dict[str, str]:
        sections: dict[str, list[str]] = {}
        current_section = "summary"

        for line in text.splitlines():
            match = SECTION_PATTERN.match(line)
            if match:
                current_section = SECTION_ALIASES[match.group(1).lower()]
                sections.setdefault(current_section, [])
                continue

            sections.setdefault(current_section, []).append(line)

        return {
            section: "\n".join(lines).strip()
            for section, lines in sections.items()
            if lines
        }

    @staticmethod
    def _extract_skills(text: str) -> list[str]:
        found_skills = []
        searchable_text = f" {text.lower()} "

        for keyword, display_name in SKILL_KEYWORDS.items():
            if ResumeParser._contains_skill(searchable_text, keyword):
                found_skills.append(display_name)

        return sorted(set(found_skills), key=str.lower)

    @staticmethod
    def _contains_skill(text: str, keyword: str) -> bool:
        escaped_keyword = re.escape(keyword.lower())
        pattern = rf"(?<![a-z0-9+#.]){escaped_keyword}(?![a-z0-9+#.])"
        return re.search(pattern, text) is not None

    @staticmethod
    def _extract_education(section_text: str) -> list[EducationItem]:
        if not section_text:
            return []

        education_items = []
        for line in ResumeParser._meaningful_lines(section_text):
            degree_match = DEGREE_PATTERN.search(line)
            year_match = YEAR_PATTERN.search(line)
            institution = ResumeParser._extract_institution(line)

            if degree_match or institution or year_match:
                education_items.append(
                    EducationItem(
                        degree=degree_match.group(0) if degree_match else None,
                        institution=institution,
                        year=year_match.group(0) if year_match else None,
                        raw_text=line,
                    ),
                )

        return education_items

    @staticmethod
    def _extract_experience(section_text: str) -> list[ExperienceItem]:
        if not section_text:
            return []

        entries = ResumeParser._group_entries(section_text)
        experience_items = []
        for entry in entries:
            first_line = entry.splitlines()[0]
            date_range = ResumeParser._extract_date_range(entry)
            title, company = ResumeParser._split_title_company(first_line)

            experience_items.append(
                ExperienceItem(
                    title=title,
                    company=company,
                    date_range=date_range,
                    raw_text=entry,
                ),
            )

        return experience_items

    @staticmethod
    def _extract_projects(section_text: str, skills: list[str]) -> list[ProjectItem]:
        if not section_text:
            return []

        projects = []
        for entry in ResumeParser._group_entries(section_text):
            first_line, _, rest = entry.partition("\n")
            description = rest.strip() or first_line.strip()
            technologies = [
                skill
                for skill in skills
                if ResumeParser._contains_skill(f" {entry.lower()} ", skill.lower())
            ]
            projects.append(
                ProjectItem(
                    name=first_line.strip(":- ") or None,
                    description=description,
                    technologies=technologies,
                ),
            )

        return projects

    @staticmethod
    def _meaningful_lines(text: str) -> list[str]:
        return [line.strip(" -•\t") for line in text.splitlines() if line.strip()]

    @staticmethod
    def _group_entries(section_text: str) -> list[str]:
        lines = ResumeParser._meaningful_lines(section_text)
        if not lines:
            return []

        entries = []
        current_entry: list[str] = []
        for line in lines:
            starts_new_entry = (
                bool(DATE_RANGE_PATTERN.search(line))
                or line.endswith(":")
                or (current_entry and not line.startswith(("-", "•")))
            )
            if starts_new_entry and current_entry:
                entries.append("\n".join(current_entry))
                current_entry = []
            current_entry.append(line)

        if current_entry:
            entries.append("\n".join(current_entry))

        return entries

    @staticmethod
    def _extract_date_range(text: str) -> str | None:
        match = DATE_RANGE_PATTERN.search(text)
        if match is None:
            return None
        return match.group(0)

    @staticmethod
    def _split_title_company(line: str) -> tuple[str | None, str | None]:
        separators = [" at ", " @ ", " - ", " | "]
        for separator in separators:
            if separator in line:
                left, right = line.split(separator, 1)
                return left.strip() or None, right.strip() or None
        return line.strip() or None, None

    @staticmethod
    def _extract_institution(line: str) -> str | None:
        institution_keywords = ("university", "college", "institute", "school")
        for part in re.split(r",|\||-", line):
            if any(keyword in part.lower() for keyword in institution_keywords):
                return part.strip()
        return None
