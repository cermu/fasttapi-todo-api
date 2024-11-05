from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.todolists.routes import todo_list_router
from src.todoitems.routes import todo_items_router
from src.systemcheck.routes import system_health_router
from src.auth.routes import auth_router
from src.db.db_setup import init_db
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    contact={
        "name": "smiling gopher",
        "email": "smilinggopher@dev.com"
    },
    lifespan=lifespan,
)

app.include_router(todo_items_router, tags=["Todo items"], prefix=settings.API_PATH_PREFIX)
app.include_router(todo_list_router, tags=["Todo lists"], prefix=settings.API_PATH_PREFIX)
app.include_router(system_health_router, tags=["Health checks"], prefix=settings.API_PATH_PREFIX)
app.include_router(auth_router, tags=["Authentication"], prefix=settings.API_PATH_PREFIX)
