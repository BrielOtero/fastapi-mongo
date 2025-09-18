from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from fastapi import HTTPException, status, Depends
from app.core.config import settings
from app.schemas.token import TokenData
from app.services.user import get_user_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_password_hash(password: str) -> str:
    """Securely hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create JWT access token with expiration"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or settings.token_expires_delta
    )
    to_encode.update({"exp": expire})
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
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        return TokenData(username=username)
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        raise credentials_exception


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """Ensure user is active and exists"""
    user = get_user_db(current_user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user
