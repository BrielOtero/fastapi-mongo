import logging
from typing import Any

from bson import ObjectId
from fastapi import HTTPException, status

from app.core.hashing import get_password_hash
from app.models.users import User, UserBase
from app.models.users import UserDB, UserDBCreate
from app.database.client import users_collection


def serialize_user_db(user: dict[str, Any]) -> UserDB:
    """Convert MongoDB document to UserDB model"""
    user["id"] = str(user["_id"])
    return UserDB(**user)


def serialize_user(user: dict[str, Any]) -> User:
    """Convert MongoDB document to User model"""
    user["id"] = str(user["_id"])
    return User(**user)


def get_users() -> list[User]:
    """Retrieve users from DB"""
    try:
        users = list(users_collection.find())
        if not users:
            return []

        return [serialize_user(user) for user in users]
    except Exception as e:
        logging.error(f"Database error during users retrieval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users",
        )


def get_user_db_by_email(email: str) -> UserDB | None:
    """Retrieve user from DB"""
    try:
        if user := users_collection.find_one({"email": email}):
            return serialize_user_db(user)
        return None
    except Exception as e:
        logging.error(f"Database error during user retrieval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        )


def get_user_by_email(email: str) -> User | None:
    """Retrieve user from DB"""
    try:
        if user := users_collection.find_one({"email": email}):
            return serialize_user(user)
        return None
    except Exception as e:
        logging.error(f"Database error during user retrieval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        )


def get_user_by_id(id: str) -> User | None:
    """Retrieve user from DB"""
    try:
        if user := users_collection.find_one({"_id": ObjectId(id)}):
            return serialize_user(user)
        return None
    except Exception as e:
        logging.error(f"Database error during user retrieval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        )


def create_user(user_in: UserDBCreate) -> UserDB:
    """Create new user with secure password handling"""
    if get_user_db_by_email(user_in.email):
        logging.warning(f"Registration attempt with existing email: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Security: Hash password BEFORE database interaction
    user_db_create = UserDBCreate(
        **user_in.model_dump(exclude={"password"}),
        password=get_password_hash(user_in.password),
    )

    logging.info(f"Creating new user: {user_db_create}")

    try:
        result = users_collection.insert_one(
            user_db_create.model_dump(by_alias=True, exclude={"id"})
        )
        created_user = users_collection.find_one({"_id": result.inserted_id})
    except Exception as e:
        logging.error(f"Database error during user creation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed",
        ) from e

    if not created_user:
        logging.critical("User created but not found in database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation succeeded but retrieval failed",
        )

    return serialize_user_db(created_user)


def retrieve_user(user_id: str, current_user: User) -> User:
    """Get user when given ID, with security checks"""
    user = get_user_by_id(user_id)
    if not user:
        logging.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"X-Error": "USER_NOT_FOUND"},
        )

    # Security: Only admins or self can view
    if not current_user.is_admin and current_user.id != user.id:
        logging.warning(
            f"Unauthorized access attempt to user {user_id} by {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
            headers={"X-Error": "PERMISSION_DENIED"},
        )

    logging.info(f"User profile accessed: {user.email}")
    return user


def retrieve_users(current_user: User) -> list[User]:
    """Retrieve all users (restricted to admin users)"""
    if not current_user.is_admin:
        logging.warning(f"Unauthorized users list attempt by: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list users",
            headers={"X-Error": "PERMISSION_DENIED"},
        )

    logging.info(f"Users list accessed by admin: {current_user.email}")
    return get_users()


def update_user(current_user: User, user_update: UserBase, user_id: str) -> User:
    # Security: Only admins or self can update
    if not current_user.is_admin and current_user.id != user_id:
        logging.warning(
            f"Unauthorized update attempt to user {user_id} by {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
            headers={"X-Error": "PERMISSION_DENIED"},
        )

    logging.info(f"User update initiated: {user_id}")

    updated = None

    try:
        updated = users_collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": user_update.model_dump(exclude={"id"})},
        )
    except Exception as e:
        logging.error(f"Database error during user update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )
    if not updated:
        logging.warning(f"User to update not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for update",
            headers={"X-Error": "USER_NOT_FOUND"},
        )

    return serialize_user(updated)


def delete_user(current_user: User, user_id: str):
    user_delete = get_user_by_id(user_id)
    if not user_delete:
        logging.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"X-Error": "USER_NOT_FOUND"},
        )

    # Security: Only admins or self can update
    if not current_user.is_admin and current_user.id != user_delete.id:
        logging.warning(
            f"Unauthorized delete attempt to user {user_delete.id} by {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
            headers={"X-Error": "PERMISSION_DENIED"},
        )

    logging.info(f"User delete initiated: {user_delete.id}")

    deleted = None

    try:
        deleted = users_collection.find_one_and_delete(
            {"_id": ObjectId(user_delete.id)}
        )
    except Exception as e:
        logging.error(f"Database error during user update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )
    if not deleted:
        logging.warning(f"User to delete not found: {user_delete.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for delete",
            headers={"X-Error": "USER_NOT_FOUND"},
        )
