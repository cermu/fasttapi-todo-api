from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from contextlib import asynccontextmanager
from src.todolists.routes import todo_list_router
from src.todoitems.routes import todo_items_router
from src.systemcheck.routes import system_health_router
from src.auth.routes import auth_router
# from src.db.db_setup import init_db
from src.utils.config import settings
from src.utils.errors import register_custom_errors


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await init_db()
#     yield

description = """
A REST API for managing ToDo list and items.

Capabilities of this API inclides:
- Create, Read, Update and Delete ToDO lists.
- Add ToDo items to a ToDo list.
"""

app = FastAPI(
    title=settings.API_TITLE,
    description=description,
    version=settings.API_VERSION,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "smiling gopher",
        "email": "smilinggopher@dev.com"
    },
    terms_of_service="https://example.com/tos",
    openapi_url=f"{settings.API_PATH_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PATH_PREFIX}/docs",
    redoc_url=f"{settings.API_PATH_PREFIX}/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"],
)

register_custom_errors(app)

app.include_router(todo_items_router, tags=["Todo items"], prefix=settings.API_PATH_PREFIX)
app.include_router(todo_list_router, tags=["Todo lists"], prefix=settings.API_PATH_PREFIX)
app.include_router(system_health_router, tags=["Health checks"], prefix=settings.API_PATH_PREFIX)
app.include_router(auth_router, tags=["Authentication"], prefix=settings.API_PATH_PREFIX)
