from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    project_name: str = "ResumeIQ API"
    api_version: str = "1.0.0"
    environment: str = "development"

    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: int = Field(3306, alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")

    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        30,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    upload_dir: Path = Field(BASE_DIR / "uploads", alias="UPLOAD_DIR")
    max_upload_size_mb: int = Field(5, alias="MAX_UPLOAD_SIZE_MB")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @computed_field
    @property
    def database_url(self) -> str:
        """Build a SQLAlchemy-compatible MySQL connection URL."""
        password = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field
    @property
    def max_upload_size_bytes(self) -> int:
        """Return the maximum allowed upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return cached settings so configuration is parsed once per process."""
    return Settings()


settings = get_settings()
