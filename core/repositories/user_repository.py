import abc
import uuid
from typing import Optional
from ..entities.user import User

class AbstractUserRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, user: User) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_credits(self, user_id: uuid.UUID, new_credit_balance: int) -> Optional[User]:
        raise NotImplementedError
