from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    surname: str
    username: str
    email: str
    age: int
    disabled: bool
