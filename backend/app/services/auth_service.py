from sqlalchemy.orm import Session

from app.auth.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.utils.exceptions import EmailAlreadyRegistered, InvalidCredentials


class AuthService:
    """Authentication use cases for registration and login."""

    @staticmethod
    def register_user(db: Session, payload: UserCreate) -> User:
        existing_user = UserService.get_by_email(db=db, email=payload.email)
        if existing_user is not None:
            raise EmailAlreadyRegistered("A user with this email already exists.")

        return UserService.create_user(
            db=db,
            full_name=payload.full_name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )

    @staticmethod
    def login_user(db: Session, payload: LoginRequest) -> str:
        user = UserService.get_by_email(db=db, email=payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentials("Incorrect email or password.")

        if not user.is_active:
            raise InvalidCredentials("User account is inactive.")

        return create_access_token(subject=str(user.id))
