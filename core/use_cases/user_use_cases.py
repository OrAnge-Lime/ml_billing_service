import uuid
from typing import Optional
from ..entities.user import User
from ..repositories.user_repository import AbstractUserRepository
from infrastructure.auth.hashing import Hasher

class UserUseCases:
    def __init__(self, user_repo: AbstractUserRepository):
        self.user_repo = user_repo
        self.hasher = Hasher()

    async def register_user(self, username: str, password: str, initial_credits: int = 10) -> User:
        existing_user = await self.user_repo.get_by_username(username)
        if existing_user:
            raise ValueError("Username already registered") 

        hashed_password = self.hasher.get_password_hash(password)
        new_user = User(
            username=username,
            hashed_password=hashed_password,
            credits=initial_credits,
            is_active=True
        )
        return await self.user_repo.add(new_user)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        return await self.user_repo.get_by_username(username)

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
         user = await self.get_user_by_username(username)
         if not user or not user.is_active:
             return None
         if not self.hasher.verify_password(password, user.hashed_password):
             return None
         return user

    async def check_user_credits(self, user_id: uuid.UUID) -> int:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found") 
        return user.credits
