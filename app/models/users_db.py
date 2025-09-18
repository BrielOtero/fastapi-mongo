from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.config import settings
from app.models.user import User


class UserDBBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    age: int = Field(ge=settings.MIN_AGE, le=120)
    is_admin: bool = False
    disabled: bool = False


class UserDBCreate(User):
    password: str = Field(min_length=settings.MIN_PASSWORD_LENGTH)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        if " " in v:
            raise ValueError("Password cannot contain spaces")
        return v


class UserDB(UserDBBase):
    id: str
    password: str

    class Config:
        from_attributes = True
