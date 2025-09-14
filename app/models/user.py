from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    surname: str
    username: str
    email: str
    age: int
    disabled: bool
