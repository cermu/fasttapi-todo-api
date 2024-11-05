from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import settings


Base = declarative_base()

# Async configuration
async_engine = create_async_engine(url=settings.POSTGRES_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Create the database tables"""
    async with async_engine.begin() as conn:
        from src.todolists.models import ToDoList
        from src.todoitems.models import ToDoItem
        from src.auth.models import User
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session():
    """Dependency to provide the session object"""
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()
# Async configuration
