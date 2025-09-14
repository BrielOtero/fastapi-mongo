from pydantic import BaseModel, Field


class UserModel(BaseModel):
    id: str | None = Field(alias="_id", default=None)
    name: str = Field(...)
    surname: str = Field(...)
    username: str = Field(...)
    email: str = Field(...)
    age: int = Field(...)
    disabled: bool = Field(...)
