import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import ToDoItem
from .schemas import ToDoItemCreate, ToDoItemUpdate


class ToDoItemService:
    """
    This class provides methods to create, read, update, and delete todo items
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_todo_item(self, id: uuid.UUID):
        """
        Get a todo item by its UUID.

        Args:
            id (uuid.UUID): the UUID of the todo item

        Returns:
            ToDoItem: the todo item object
        """
        query = select(ToDoItem).where(ToDoItem.id == id)
        results = await self.session.execute(query)
        return results.scalar_one_or_none()

    async def get_todo_items(self, skip: int = 0, limit: int = 100):
        """
        Get a list of all todo items

        Returns:
            list: list of todo items
        """
        query = select(ToDoItem).offset(skip).limit(limit)
        results = await self.session.execute(query)
        return results.scalars().all()

    async def create_todo_item(self, todo_item: ToDoItemCreate):
        """
        Create a new todo item

        Args:
            todo_item (ToDoItemCreate schema): data to create a new todo item

        Returns:
            ToDoItem: the new todo item
        """
        new_todo_item = ToDoItem(
            name=todo_item.name,
            description=todo_item.description,
            todolist_id=todo_item.todolist_id,
            is_complete=todo_item.is_complete
        )
        self.session.add(new_todo_item)
        await self.session.commit()
        await self.session.refresh(new_todo_item)
        return new_todo_item
    
    async def update_todo_item(self, id: str, todo_item_update_data: ToDoItemUpdate):
        """
        Update a todo item

        Args:
            id (str): the id of the todo item
            todo_item_update_data (ToDoItemCreate schema): data to update an existing todo item

        Returns:
            ToDoItem: the updated todo item
        """
        query = select(ToDoItem).where(ToDoItem.id == id)
        results = await self.session.execute(query)
        existing_item = results.scalar_one_or_none()

        if not existing_item:
            return None
        
        for key, value in todo_item_update_data.model_dump(exclude_unset=True).items():
            setattr(existing_item, key, value)
        await self.session.commit()
        return existing_item
        
    async def delete_todo_item(self, id: str):
        """
        Delete a todo item

        Args:
            id (str): the id of the todo item
        """
        query = select(ToDoItem).where(ToDoItem.id == id)
        results = await self.session.execute(query)
        existing_item = results.scalars().first()

        if not existing_item:
            return None
        await self.session.delete(existing_item)
        await self.session.commit()
        return {}
