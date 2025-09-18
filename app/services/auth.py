import logging
from typing import Any
from fastapi import HTTPException, status
from app.models.users_db import UserDB
from app.services.user import get_user_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings


def authenticate_user(email: str, password: str) -> UserDB:
    """Authenticate user and return user object"""
    user = get_user_db(email)
    if not user:
        logging.warning(f"Login failed - user not found: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, user.password):
        logging.warning(f"Login failed - invalid password for user: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logging.info(f"Successful authentication for user: {email}")
    return user


def login_for_access_token(email: str, password: str) -> dict[str, Any]:
    """Generate access token for authenticated user"""
    user = authenticate_user(email, password)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=settings.token_expires_delta
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
