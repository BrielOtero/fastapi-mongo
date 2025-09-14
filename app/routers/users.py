import logging
from fastapi import APIRouter, HTTPException, status
from app.models.user import UserModel
from app.database.client import users_collection
from app.schemas.user import UserCreate

users_list: list[UserModel] = []

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


def search_user(id: str) -> UserModel | None:
    return next((u for u in users_list if u.id == id), None)


def search_user_by_email(email: str) -> UserModel | None:
    try:
        user = users_collection.find_one({"email": email})
        if not user:
            return None

        return UserModel(**user)
    except Exception as e:
        logging.warning(f"User not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created user",
        )


# GET /users/
@router.get("/")
async def read_users() -> list[UserModel]:
    return users_list


# GET /users/id
@router.get("/{id}")
async def read_user(id: str) -> UserModel:
    user = search_user(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# POST /users/
@router.post("/")
async def post_user(user: UserCreate) -> UserModel:
    existing_user = search_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user_dict = user.model_dump()

    result = users_collection.insert_one(user_dict)

    inserted_user = users_collection.find_one({"_id": result.inserted_id})

    if inserted_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created user",
        )
    inserted_user["_id"] = str(inserted_user["_id"])

    return UserModel(**inserted_user)


# PUT /users/
@router.put("/")
async def put_user(user: UserModel) -> UserModel:
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
async def delete_user(id: str) -> list[UserModel]:
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
