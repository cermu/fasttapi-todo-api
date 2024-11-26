import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import ToDoList
from .schemas import ToDoListCreate, ToDoListUpdate


class ToDoListService:
    """
    This class provides methods to create, read, update, and delete todo lists
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_todo_list(self, id: uuid.UUID):
        """
        Get a todo list by its UUID.

        Args:
            id (uuid.UUID): the UUID of the todo list

        Returns:
            ToDoList: the todo list object
        """
        query = select(ToDoList).where(ToDoList.id == id)
        results = await self.session.execute(query)
        return results.scalar_one_or_none()

    async def get_todo_lists(self, skip: int = 0, limit: int = 100):
        """
        Get a list of all todo lists

        Returns:
            list: list of todo lists
        """
        query = select(ToDoList).offset(skip).limit(limit)
        results = await self.session.execute(query)
        return results.scalars().all()

    async def create_todo_list(self, todo_list: ToDoListCreate):
        """
        Create a new todo list

        Args:
            todo_list (ToDoListCreate schema): data to create a new todo list

        Returns:
            ToDoList: the new todo list
        """
        new_todo_list = ToDoList(
            title=todo_list.title,
            is_active=todo_list.is_active
        )
        self.session.add(new_todo_list)
        await self.session.commit()
        await self.session.refresh(new_todo_list)
        return new_todo_list

    async def update_todo_list(self, id: uuid.UUID, todo_list_update_data: ToDoListUpdate):
        """
        Update a book

        Args:
            id (uuid.UUID): the UUID of the todo list
            todo_list_update_data (ToDoList schema): the data to update an existing todo list

        Returns:
            ToDoList: the updated todo list
        """
        query = select(ToDoList).where(ToDoList.id == id)
        results = await self.session.execute(query)
        existing_todo_list = results.scalars().first()
        
        if not existing_todo_list:
            return None
            
        for key, value in todo_list_update_data.model_dump(exclude_unset=True).items():
            setattr(existing_todo_list, key, value)
        await self.session.commit()
        return existing_todo_list

    async def delete_todo_list(self, id: uuid.UUID):
        """
        Delete a todo list

        Args:
            id (uuid.UUID): the UUID of the todo list
        """
        query = select(ToDoList).where(ToDoList.id == id)
        results = await self.session.execute(query)
        existing_todo_list = results.scalars().first()

        if not existing_todo_list:
            return {}
        await self.session.delete(existing_todo_list)
        await self.session.commit()
        return {}