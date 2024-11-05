from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.orm import declarative_mixin
import sqlalchemy.dialects.postgresql as pg


@declarative_mixin
class Timestamp:
    created_at = Column(pg.TIMESTAMP, default=datetime.now, nullable=False)
    updated_at = Column(pg.TIMESTAMP, default=datetime.now, nullable=False, onupdate=datetime.now)
