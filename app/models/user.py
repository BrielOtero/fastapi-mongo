from app.models.users_db import UserDBBase


class User(UserDBBase):
    id: str | None

    class Config:
        from_attributes = True
