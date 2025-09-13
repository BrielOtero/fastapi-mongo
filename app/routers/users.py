from fastapi import APIRouter, HTTPException, status
from app.models.user import User

users_list = [
    User(
        id=1,
        name="Gabriel",
        surname="Otero",
        email="email@email.com",
        age=28,
        disabled=False,
    )
]

router = APIRouter(prefix="/users", tags=["users"])


def search_user(id: int) -> User | None:
    return next((u for u in users_list if u.id == id), None)


# GET /users/
@router.get("/")
async def read_users() -> list[User]:
    return users_list


# GET /users/id
@router.get("/{id}")
async def read_user(id: int) -> User:
    user = search_user(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# POST /users/
@router.post("/")
async def post_user(user: User) -> User:
    users_list.append(user)
    return user


# PUT /users/
@router.put("/")
async def put_user(user: User) -> User:
    updated = False
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            updated = True
            break

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# DELETE /users/id
@router.delete("/{id}")
async def delete_user(id: int) -> list[User]:
    deleted = False
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            deleted = True
            break

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return users_list
