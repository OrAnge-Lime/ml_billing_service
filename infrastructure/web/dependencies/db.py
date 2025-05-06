from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.db.database import AsyncSessionFactory

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a SQLAlchemy AsyncSession."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
