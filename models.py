from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


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


class Walkins(BaseModel):
    id: int
    name: str
    area: Optional[str] = None
    pin: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    team: Optional[str] = None
    status: Optional[str] = None
    categor: Optional[str] = None
    products: Optional[str] = None
    store: str
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    amount: Optional[float] = 0
    followup: Optional[int] = 0

class Store(BaseModel):
    id: int
    sym: str
    name: str

class Status(BaseModel):
    id: int
    status: str

class Staff(BaseModel):
    id: int
    name: str
    sym: str

class Categor(BaseModel):
    id: int
    name: str
    sym: str