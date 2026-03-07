from pydantic import BaseModel
from typing import List


class RegisterModel(BaseModel):
    name: str
    password: str
    type: str


class LoginModel(BaseModel):
    name: str
    password: str


class Action(BaseModel):
    id: int
    name: str
    description: str
    level: int


class User(BaseModel):
    id: int
    name: str
    type: str
    roles: str


class UpdateUserRoles(BaseModel):
    id: int
    roles: List[int]