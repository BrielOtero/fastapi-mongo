from fastapi import APIRouter, status, Depends
from app.core.security import get_current_active_user
from app.models.users import User, UserBase, UserDBCreate

from app.schemas.auth_form import AuthForm
from app.models.token import Token
from app.services.auth import login_for_access_token
from app.services.users import (
    create_user,
    delete_user,
    retrieve_user,
    retrieve_users,
    update_user,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# POST /users/register
@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
async def register(user: UserDBCreate):
    return create_user(user)


# POST /users/login
@router.post(
    "/login",
    response_model=Token,
)
async def login(form_data: AuthForm = Depends()) -> Token:
    """Authenticate user and return access token"""
    return login_for_access_token(form_data)


# GET /users/me
@router.get(
    "/me",
    response_model=User,
)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Retrieve current authenticated user's profile"""
    return current_user


# GET /users
@router.get(
    "/",
    response_model=list[User],
)
async def list_users(
    current_user: User = Depends(get_current_active_user),
) -> list[User]:
    return retrieve_users(current_user)


# GET /users/{user_id}
@router.get(
    "/{user_id}",
    response_model=User,
)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Retrieve a specific user by ID"""
    return retrieve_user(user_id, current_user)


# PUT /users/{user_id}
@router.put("/{user_id}", response_model=User)
async def update_user_profile(
    user_id: str,
    user_update: UserBase,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Update user profile with partial data"""
    return update_user(current_user, user_update, user_id)


# DELETE /users/{user_id}
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_account(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    # """Delete user account (admins can delete others, users can delete themselves)"""
    delete_user(current_user, user_id)
