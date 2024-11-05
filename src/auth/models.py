import uuid
from typing import Optional
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from src.db.db_setup import Base
from src.db.mixins import Timestamp


class User(Timestamp, Base):
    __tablename__ = "users"
    id: uuid.UUID = Column(UUID, default=uuid.uuid4, primary_key=True, index=True, unique=True)
    username: str = Column(String(250), nullable=False, index=True, unique=True)
    email: str = Column(String(250), nullable=False, index=True, unique=True)
    password: str = Column(String(300), nullable=False)
    first_name: Optional[str] = Column(String(250), nullable=True)
    last_name: Optional[str] = Column(String(250), nullable=True)
    is_active: bool = Column(Boolean, default=True)
