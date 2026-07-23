from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str


class TodoItemCreate(BaseModel):
    title: str
    description: str | None = None


class TodoItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoItemRead(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    user_id: int
    created_at: datetime
    updated_at: datetime


class TodoItemListRead(BaseModel):
    items: list[TodoItemRead]
    page: int
    limit: int
    total: int


class TokenRead(BaseModel):
    token: str
