from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import User

router = APIRouter(prefix="/basic-auth", tags=["basic_auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class UserDB(User):
    password: str


users_db: dict[str, UserDB] = {
    "gabriel": UserDB(
        id=1,
        name="gabriel",
        surname="otero",
        email="email@email.com",
        age=28,
        disabled=False,
        password="123456",
    ),
    "gabriel2": UserDB(
        id=2,
        name="gabriel2",
        surname="otero2",
        email="email2@email.com",
        age=29,
        disabled=True,
        password="654321",
    ),
}


def search_user_db(username: str) -> UserDB | None:
    user_db = users_db.get(username)
    if user_db:
        return user_db
    return None


def search_user(username: str) -> User | None:
    user_db = users_db.get(username)
    if user_db:
        return User(**user_db.model_dump(exclude={"password"}))

    return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user = search_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = search_user_db(form.username)

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if form.password != user_db.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    return {"access_token": user_db.name, "token_type": "bearer"}


@router.get("/me")
async def read_users_me(user: User = Depends(get_current_user)) -> User:
    return user
