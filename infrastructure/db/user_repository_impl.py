import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # Keep import here

from core.entities.user import User
from core.repositories.user_repository import AbstractUserRepository
from .models import UserDB


class SQLAlchemyUserRepository(AbstractUserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session  # Store session injected via constructor

    def _to_entity(self, db_user: UserDB) -> User | None:
        """Converts DB model instance to User entity."""
        if not db_user:
            return None
        return User(
            id=db_user.id,
            username=db_user.username,
            hashed_password=db_user.hashed_password,
            credits=db_user.credits,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
        )

    def _to_db_model(self, user: User) -> UserDB:
        """Converts User entity to DB model instance for inserts/updates."""
        return UserDB(
            id=user.id,
            username=user.username,
            hashed_password=user.hashed_password,
            credits=user.credits,
            is_active=user.is_active,
            is_admin=user.is_admin,
        )

    async def add(self, user: User) -> User:
        """Adds a new user to the database using the stored session."""
        db_user = self._to_db_model(user)
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return self._to_entity(db_user)

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Gets a user by ID using the stored session."""
        stmt = select(UserDB).where(UserDB.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user)

    async def get_by_id_for_update(self, user_id: uuid.UUID) -> Optional[User]:
        """Gets a user by ID with a lock for update using the stored session."""
        stmt = select(UserDB).where(UserDB.id == user_id).with_for_update()
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Gets a user by username using the stored session."""
        stmt = select(UserDB).where(UserDB.username == username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return self._to_entity(db_user)

    async def update_credits(
        self, user_id: uuid.UUID, new_credit_balance: int
    ) -> Optional[User]:
        """Updates user credits using the stored session."""
        stmt = select(UserDB).where(UserDB.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if db_user:
            db_user.credits = new_credit_balance
            await self.session.flush()
            # No refresh needed typically unless reading back immediately within same complex logic block
            return self._to_entity(db_user)
        return None
