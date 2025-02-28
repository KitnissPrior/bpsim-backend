from pydantic import BaseModel
from typing import Optional


# class UserBase(BaseModel):
#     username: str
#     email: str
#
# class UserCreate(UserBase):
#     pass
#
# class User(UserBase):
#     id: Optional[int] = None
#
#     class Config:
#         orm_mode = True

class User(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True

class Node(BaseModel):
    name: str | None = None
    description: str | None = None
    posX: float | None = None
    posY: float | None = None

    class Config:
        orm_mode = True