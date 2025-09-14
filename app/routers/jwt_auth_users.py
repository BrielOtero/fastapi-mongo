import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.models.user import User
from passlib.context import CryptContext
from typing import Any
import jwt
from jwt import DecodeError, ExpiredSignatureError


SECRET_KEY = "22a98070516e123bf0edf965f6fad38af4f27ccdc48b55e673f292de936e5093"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class UserDB(User):
    password: str


users_db: dict[str, UserDB] = {
    "gabriel": UserDB(
        id=1,
        name="gabriel",
        surname="otero",
        username="gabriel",
        email="email@email.com",
        age=28,
        disabled=False,
        password="$2a$12$tSWQO79a6Ky3OHkQAxELpubUpL4fIY7APJ2nrib2Gl0o7HShSMSdm",
    ),
    "gabriel2": UserDB(
        id=2,
        name="gabriel2",
        surname="otero2",
        username="gabriel2",
        email="email2@email.com",
        age=29,
        disabled=True,
        password="$2a$12$jYRDFxf4.kAJ/z9L/uyI7egSavhux4lPhJ8xAnyLgfo4DsU/XmM.a",
    ),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_user_db(username: str) -> UserDB | None:
    """Get a user from the database by username."""
    user_db = users_db.get(username)
    if user_db:
        return user_db

    return None


async def authenticate_user(token: str = Depends(oauth2_scheme)) -> User:
    """Authenticate a user based on a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")

        if not username:
            logging.warning("Token missing subject")
            raise credentials_exception

        token_data = TokenData(username=str(username))

    except ExpiredSignatureError:
        logging.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except DecodeError:
        logging.warning("Token decode error")
        raise credentials_exception
    except Exception as e:
        logging.error(f"Unexpected error during token validation: {e}")
        raise credentials_exception

    user = get_user_db(username=token_data.username)
    if user is None:
        logging.warning(f"User not found: {token_data.username}")
        raise credentials_exception

    logging.info(f"Successfully authenticated user: {user.username}")
    return user


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return str(encoded_jwt)


async def get_current_active_user(
    current_user: User = Depends(authenticate_user),
) -> User:
    """Get the current active user, raising an exception if the user is disabled."""
    if current_user.disabled:
        logging.warning(f"Attempt to access disabled user: {current_user.username}")
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Login endpoint that authenticates a user and returns a JWT token."""
    logging.info(f"Login attempt for user: {form.username}")

    user_db = get_user_db(form.username)
    if not user_db:
        logging.warning(f"Login failed - user not found: {form.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form.password, user_db.password):
        logging.warning(f"Login failed - invalid password for user: {form.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user_db.username}, expires_delta=access_token_expires
    )

    logging.info(f"Successful login for user: {user_db.username}")
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Return the current authenticated user's information."""
    logging.info(f"User info requested for: {current_user.username}")
    return current_user
