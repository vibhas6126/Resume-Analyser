from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserService:
    """Database operations for user accounts."""

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        normalized_email = email.lower().strip()
        statement = select(User).where(User.email == normalized_email)
        return db.scalar(statement)

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def create_user(
        db: Session,
        full_name: str,
        email: str,
        hashed_password: str,
    ) -> User:
        user = User(
            full_name=full_name.strip(),
            email=email.lower().strip(),
            hashed_password=hashed_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
