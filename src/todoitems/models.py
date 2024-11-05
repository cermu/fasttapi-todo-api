import uuid
from typing import Optional
from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.db.db_setup import Base
from src.db.mixins import Timestamp


class ToDoItem(Timestamp, Base):
    __tablename__ = "todoitems"
    id: uuid.UUID = Column(UUID, default=uuid.uuid4, primary_key=True, index=True, unique=True)
    name: str = Column(String(250), nullable=False, index=True)
    description: Optional[str] = Column(Text, nullable=True)
    is_complete: bool = Column(Boolean, default=False)
    todolist_id: uuid.UUID = Column(UUID, ForeignKey("todolist.id"), nullable=False)

    list = relationship("ToDoList", back_populates="items", lazy="selectin")
