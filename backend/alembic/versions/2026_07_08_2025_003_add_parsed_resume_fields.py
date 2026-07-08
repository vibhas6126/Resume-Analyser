"""add parsed resume fields

Revision ID: 003
Revises: 002
Create Date: 2026-07-08 20:25:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("resumes", sa.Column("extracted_skills", sa.JSON(), nullable=True))
    op.add_column("resumes", sa.Column("extracted_education", sa.JSON(), nullable=True))
    op.add_column("resumes", sa.Column("extracted_experience", sa.JSON(), nullable=True))
    op.add_column("resumes", sa.Column("extracted_projects", sa.JSON(), nullable=True))
    op.add_column(
        "resumes",
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("resumes", "parsed_at")
    op.drop_column("resumes", "extracted_projects")
    op.drop_column("resumes", "extracted_experience")
    op.drop_column("resumes", "extracted_education")
    op.drop_column("resumes", "extracted_skills")
