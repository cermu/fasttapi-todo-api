import uuid
import fastapi
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from .schemas import ToDoItemCreate, ToDoItem, ToDoItemUpdate
from .service import ToDoItemService
from src.utils.errors import (
    InternalServerErrorException,
)

todo_items_router = fastapi.APIRouter(prefix="/todoitems")


@todo_items_router.get("/", response_model=List[ToDoItem], status_code=status.HTTP_200_OK)
async def read_todo_items(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_async_session)):
    try:
        return await ToDoItemService(session).get_todo_items(skip=skip, limit=limit)
    except Exception as e:
        print("===================================")
        print(f"Request processing error: {str(e)}")
        print("===================================")
        raise InternalServerErrorException()

@todo_items_router.post("/", response_model=ToDoItem, status_code=status.HTTP_201_CREATED)
async def create_new_todo_item(item: ToDoItemCreate, session: AsyncSession = Depends(get_async_session)):
    return await ToDoItemService(session).create_todo_item(todo_item=item)

@todo_items_router.get("/{id}", response_model=ToDoItem, status_code=status.HTTP_200_OK)
async def read_todo_item(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    results = await ToDoItemService(session).get_todo_item(id=id)
    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    return results

@todo_items_router.put("/{id}", response_model=ToDoItem, status_code=status.HTTP_200_OK)
async def modify_todo_item(id: str, update_data: ToDoItemUpdate, session: AsyncSession = Depends(get_async_session)):
    results = await ToDoItemService(session).update_todo_item(id=id, todo_item_update_data=update_data)
    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    return results

@todo_items_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy_todo_item(id: str, session: AsyncSession = Depends(get_async_session)):
    results = await ToDoItemService(session).delete_todo_item(id=id)
    if results is None:
        return
    return
