import uuid
import fastapi
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_setup import get_async_session
from .service import ToDoListService
from .schemas import ToDoListCreate, ToDoList, ToDoListUpdate

todo_list_router = fastapi.APIRouter(prefix="/todolists")


@todo_list_router.get("/", response_model=List[ToDoList], status_code=status.HTTP_200_OK)
async def read_todo_lists(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_async_session)):
    return await ToDoListService(session).get_todo_lists(skip=skip, limit=limit)

@todo_list_router.post("/", response_model=ToDoList, status_code=status.HTTP_201_CREATED)
async def create_new_todo_list(list: ToDoListCreate, session: AsyncSession = Depends(get_async_session)):
    return await ToDoListService(session).create_todo_list(todo_list=list)

@todo_list_router.get("/{id}", response_model=ToDoList, status_code=status.HTTP_200_OK)
async def read_todo_list(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    results = await ToDoListService(session).get_todo_list(id=id)
    if results is None:
        raise HTTPException(status_code=404, detail="Todo list not found")
    return results

@todo_list_router.put("/{id}", response_model=ToDoList, status_code=status.HTTP_200_OK)
async def modify_todo_list(id: uuid.UUID, update_data: ToDoListUpdate, session: AsyncSession = Depends(get_async_session)):
    results = await ToDoListService(session).update_todo_list(id=id, todo_list_update_data=update_data)
    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo list not found")
    return results

@todo_list_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy_todo_list(id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    await ToDoListService(session).delete_todo_list(id=id)
    return
