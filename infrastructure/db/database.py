from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

try:
    # основной интерфейс для асинхронного взаимодействия с БД на низком уровне. Управляет пулом соединений.
    engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True) 
    AsyncSessionFactory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False, # Important for async usage
        autoflush=False,
        autocommit=False
    )
    logger.info("Async database engine and session factory created successfully.")
except Exception as e:
    logger.exception(f"Failed to create database engine or session factory: {e}")
    raise

Base = declarative_base() # базовый класс для декларативного определения ORM-моделей

async def get_db_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # Implicitly commits if no exceptions raised by the endpoint handler
            # await session.commit() # Usually not needed if session context manager is used correctly
        except Exception:
            await session.rollback()
            raise
        finally:
            # The session is automatically closed by the context manager 'async with' dk_
            pass # await session.close() # Not needed with async with AsyncSessionFactory() as session

async def create_tables():
    async with engine.begin() as conn: # dk_
        # await conn.run_sync(Base.metadata.drop_all)
        # создает все таблицы, которые унаследованы от Base, если не существуют.
        await conn.run_sync(Base.metadata.create_all) 
    logger.info("Database tables checked/created.")
