from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database.connection import get_db
from app.models.user import User
from app.services.user_service import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from a bearer JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    subject = decode_access_token(token)
    if subject is None:
        raise credentials_exception

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise credentials_exception from exc

    user = UserService.get_by_id(db=db, user_id=user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user
