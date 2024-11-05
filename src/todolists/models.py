import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.db.db_setup import Base
from src.db.mixins import Timestamp


class ToDoList(Timestamp, Base):
    __tablename__ = "todolist"
    id: uuid.UUID = Column(UUID, default=uuid.uuid4, primary_key=True, index=True, unique=True)
    title: str = Column(String(250), nullable=False)
    is_active: bool = Column(Boolean, default=True)

    items = relationship("ToDoItem", back_populates="list", lazy="selectin", cascade="all,delete")
