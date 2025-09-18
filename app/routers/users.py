import logging
from typing import Any
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.users_db import UserDBCreate

from app.services.auth import login_for_access_token
from app.services.user import create_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# GET /users/
@router.get("/", response_model=list[User], response_model_by_alias=False)
async def read_users():
    return retrieve_users()


# GET /users/id
@router.get("/{id}", response_model=User)
async def read_user(id: str):
    user = retrieve_user(id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# POST /users/
@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
async def register(user: UserDBCreate):
    return create_user(user)


@router.post(
    "/login",
)
def login(email: str, password: str) -> dict[str, Any]:
    """Authenticate user and return access token"""
    return login_for_access_token(email, password)


@router.get(
    "/me",
    response_model=User,
)
def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Retrieve current authenticated user's profile"""
    return current_user


@router.get(
    "/",
    response_model=list[User],
)
def list_users(
    current_user: User = Depends(get_current_active_user),
) -> list[User]:
    """Retrieve all users (restricted to admin users)"""
    if not current_user.is_admin:  # Assuming you have an is_admin field
        logging.warning(f"Unauthorized users list attempt by: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list users",
            headers={"X-Error": "PERMISSION_DENIED"},
        )

    # In real implementation, you'd fetch from database
    # This is a placeholder for the actual implementation
    logging.info(f"Users list accessed by admin: {current_user.email}")
    return []  # Actual implementation would return users


@router.get(
    "/{user_id}",
    response_model=User,
)
def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Retrieve a specific user by ID"""
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


@router.put("/{user_id}", response_model=User)
def update_user_profile(
    user_update: User,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Update user profile with partial data"""
    # Security: Only admins or self can update
    if not current_user.is_admin and current_user.id != user_update.id:
        logging.warning(
            f"Unauthorized update attempt to user {user_update.id} by {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
            headers={"X-Error": "PERMISSION_DENIED"},
        )

    logging.info(f"User update initiated: {user_update.id}")
    return update_user(user_update)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_account(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete user account (admins can delete others, users can delete themselves)"""
    # Security: Only admins can delete others
    if current_user.id != user_id and not current_user.is_admin:
        logging.warning(
            f"Unauthorized delete attempt for user {user_id} by {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
            headers={"X-Error": "PERMISSION_DENIED"},
        )

    logging.info(f"User deletion initiated: {user_id}")
    delete_user(user_id)
