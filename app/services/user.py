import logging
from typing import Any

from fastapi import HTTPException, status

from app.core.security import get_password_hash
from app.models.users_db import UserDB, UserDBCreate
from app.database.client import users_collection


def serialize_user_db(user: dict[str, Any]) -> UserDB:
    """Convert MongoDB document to UserDB model"""
    user["id"] = str(user["_id"])
    return UserDB(**user)


def get_user_db(email: str) -> UserDB | None:
    """Retrieve user from DB (internal use only)"""
    if user := users_collection.find_one({"email": email}):
        return serialize_user_db(user)
    return None


def create_user(user_in: UserDBCreate) -> UserDB:
    """Create new user with secure password handling"""
    if get_user_db(user_in.email):
        logging.warning(f"Registration attempt with existing email: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Security: Hash password BEFORE database interaction
    user_db = UserDB(
        **user_in.model_dump(), password=get_password_hash(user_in.password)
    )

    try:
        result = users_collection.insert_one(user_db.model_dump(by_alias=True))
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
