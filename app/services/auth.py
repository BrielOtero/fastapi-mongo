from app.core.logger import logger
from fastapi import HTTPException, status
from app.models.users import User
from app.schemas.auth_form import AuthForm
from app.models.token import Token
from app.services.users import get_user_db_by_email
from app.core.hashing import verify_password
from app.core.security import create_access_token
from app.core.config import settings


def authenticate_user(email: str, password: str) -> User:
    """Authenticate user and return user object"""
    user = get_user_db_by_email(email)
    if not user:
        logger.warning(f"Login failed - user not found: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, user.password):
        logger.warning(f"Login failed - invalid password for user: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Successful authentication for user: {email}")
    return User(**user.model_dump())


def login_for_access_token(form_data: AuthForm) -> Token:
    """Generate access token for authenticated user"""
    user = authenticate_user(form_data.email, form_data.password)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=settings.token_expires_delta
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
