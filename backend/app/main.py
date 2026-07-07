from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    description="AI Resume Analyzer Backend",
    version=settings.api_version,
)

app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Welcome to ResumeIQ API!"
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "Running"
    }
