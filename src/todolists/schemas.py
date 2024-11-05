import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel
from src.todoitems.schemas import ToDoItem


class ToDoListBase(BaseModel):
    title: str
    is_active: bool


class ToDoListCreate(ToDoListBase):
    pass


class ToDoListUpdate(BaseModel):
    title: str | None = None
    is_active: bool | None = None


class ToDoList(ToDoListBase):
    id: uuid.UUID
    items: List[ToDoItem] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
