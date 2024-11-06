from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User
from .schemas import UserSignUp, UserUpdate, UserLogin, UserExist
from src.auth.utils import verify_password, get_password_hash


class UserService:
    """
    This class provides methods to create, read, update, and delete users
    """

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_username(self, username: str):
        """
        Get a user by their username

        Args:
            username (str): provided username

        Returns:
            User: the newly created user
        """
        query = select(User).where(User.username == username)
        results = await self.session.execute(query)
        return results.scalars().first()
    
    async def get_user_by_email(self, email: str):
        """
        Get a user by their email

        Args:
            email (str): provided email

        Returns:
            User: the newly created user
        """
        query = select(User).where(User.email == email)
        results = await self.session.execute(query)
        return results.scalars().first()
    
    async def create_user(self, user: UserSignUp):
        """
        Create a new user

        Args:
            user (UserSignUp schema): data to create a new user

        Returns:
            User: the newly created user
        """
        username_exists = await self.get_user_by_username(user.username)
        email_exists = await self.get_user_by_email(user.email)
        
        if username_exists:
            return UserExist(message="user with the provided data already exist", status="failed")
        
        if email_exists:
            return UserExist(message="user with the provided data already exist", status="failed")
        
        hashed_password = get_password_hash(user.password)
        
        new_user = User(
            username=user.username,
            password=hashed_password,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
    
    async def authenticate_user(self, username: str, password: str):
        """
        Authenticate/login a user

        Args:
            username (str): user provided username
            password (str): user provided password

        Returns:
            User: authenticated user
        """
        query = select(User).where(User.username == username)
        results = await self.session.execute(query)
        existing_user = results.scalars().first()

        if not existing_user:
            return False
        if not verify_password(password, existing_user.password):
            return False
        return existing_user
    
    async def get_users(self, offset: int = 0, limit: int = 100):
        """
        Get a list of users

        Returns:
            list: list of users
        """
        query = select(User).offset(offset).limit(limit)
        results = await self.session.execute(query)
        return results.scalars().all()
