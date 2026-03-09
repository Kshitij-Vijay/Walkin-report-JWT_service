from pydantic import BaseModel, EmailStr
from typing import List


class LogModel(BaseModel):
    username: str
    query: str
    description: str | None = None
    status: str


class RegisterModel(BaseModel):
    name: str
    password: str
    type: str
    email : str


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