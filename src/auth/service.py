from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User
from .schemas import UserSignUp, UserUpdate, UserExist, AdminSignUp
from .utils import (
    get_password_hash, verify_password,
    send_user_verification_email,
)

class UserService:
    """
    This class provides methods to create, read, update, and delete users
    """

    def __init__(self):
        pass

    async def get_user_by_id(self, session: AsyncSession, id: str):
        """
        Get a user by their id

        Args:
            id (str): provided user id

        Returns:
            User: an existing user
        """
        query = select(User).where(User.id == id)
        results = await session.execute(query)
        return results.scalars().first()
    
    async def get_user_by_username(self, session: AsyncSession, username: str):
        """
        Get a user by their username

        Args:
            username (str): provided username

        Returns:
            User: an existing user
        """
        query = select(User).where(User.username == username)
        results = await session.execute(query)
        return results.scalars().first()
    
    async def get_user_by_email(self, session: AsyncSession, email: str):
        """
        Get a user by their email

        Args:
            email (str): provided email

        Returns:
            User: an existing user
        """
        query = select(User).where(User.email == email)
        results = await session.execute(query)
        return results.scalars().first()
    
    async def create_user(self, session: AsyncSession, user: Union[UserSignUp, AdminSignUp]):
        """
        Create a new user

        Args:
            user (UserSignUp schema): data to create a new user

        Returns:
            User: the newly created user
        """
        username_exists = await self.get_user_by_username(session, user.username)
        email_exists = await self.get_user_by_email(session, user.email)
        
        if username_exists:
            return UserExist(message="user with the provided data already exist", error_code="CE006")
        
        if email_exists:
            return UserExist(message="user with the provided data already exist", error_code="CE006")
        
        hashed_password = get_password_hash(user.password)
        
        new_user = User(
            username=user.username,
            password=hashed_password,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        )
        if isinstance(user, AdminSignUp):
            new_user.role=user.role
            new_user.is_verified=user.is_verified
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    async def authenticate_user(self, session: AsyncSession, username: str, password: str):
        """
        Authenticate/login a user

        Args:
            username (str): user provided username
            password (str): user provided password

        Returns:
            User: authenticated user
        """
        query = select(User).where(User.username == username)
        results = await session.execute(query)
        existing_user = results.scalars().first()

        if not existing_user:
            return False
        if not verify_password(password, existing_user.password):
            return False
        return existing_user
    
    async def get_users(self, session: AsyncSession, offset: int = 0, limit: int = 100):
        """
        Get a list of users

        Returns:
            list: list of users
        """
        query = select(User).offset(offset).limit(limit)
        results = await session.execute(query)
        return results.scalars().all()
    
    async def update_user(self, session: AsyncSession, user: User, update_data: dict):
        """
        Update an existing user

        Args:
            user (User): an existing user object
            update_data (dict): provided data ti update a user

        Returns:
            User: an updated user object
        """
        for k, v in update_data.items():
            setattr(user, k, v)
        await session.commit()
        return user
    
    async def modify_user_logic(self, session: AsyncSession, send_verification_email: bool, existing_user: User, current_user: User, update_data: UserUpdate):
        if current_user.role == "user":
            update_data.role = existing_user.role
            update_data.is_active = existing_user.is_active
            update_data.is_verified = existing_user.is_verified
        
        if send_verification_email:
            update_data.is_verified = False
            await self.update_user(session, existing_user, update_data.model_dump(exclude_unset=True))

            send_user_verification_email(email=update_data.email)
            return {
                "message": "user has been updated successfully! Check email to verify your account.",
                "user": existing_user
            }
        
        await self.update_user(session, existing_user, update_data.model_dump(exclude_unset=True))
        return {
            "message": "user has been updated successfully.",
            "user": existing_user
        }
    
    async def delete_user(self, session: AsyncSession, id: str):
        """
        Delete a user

        Args:
            id (str): the id of the user to delete
        """
        query = select(User).where(User.id == id)
        results = await session.execute(query)
        existing_user = results.scalars().first()

        if not existing_user:
            return {}
        await session.delete(existing_user)
        await session.commit()
        return {}
