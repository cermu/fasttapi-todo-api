import uuid
from datetime import datetime
from pydantic import BaseModel


class ToDoItemBase(BaseModel):
    name: str
    description: str
    is_complete: bool


class ToDoItemCreate(ToDoItemBase):
    todolist_id: uuid.UUID


class ToDoItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_complete: bool | None = None
    todolist_id: uuid.UUID | None = None


class ToDoItem(ToDoItemBase):
    id: uuid.UUID
    todolist_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
