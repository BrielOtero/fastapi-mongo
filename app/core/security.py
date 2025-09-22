import logging
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from fastapi import HTTPException, status, Depends
from app.core.config import settings
from app.models.token import TokenData, TokenPayload
from app.services.users import get_user_by_email
from app.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create JWT access token with expiration"""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or settings.token_expires_delta)
    to_encode.update({"iat": now, "exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return str(encoded_jwt)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Validate token and extract user data"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        jwt_payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        payload = TokenPayload(**jwt_payload)
        email: str = payload.sub
        if not email:
            raise credentials_exception
        return TokenData(email=email)
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError) as e:
        logging.error(f"Token validation error: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
) -> User:
    """Ensure user is active and exists"""
    user = get_user_by_email(current_user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user
