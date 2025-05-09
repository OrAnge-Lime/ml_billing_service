import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession # Keep import here

from core.entities.ml_model import MLModel
from core.repositories.ml_model_repository import AbstractMLModelRepository
from .models import MLModelDB

class SQLAlchemyMLModelRepository(AbstractMLModelRepository):

    def __init__(self, session: AsyncSession):
        self.session = session 

    def _to_entity(self, db_model: MLModelDB) -> MLModel | None:
        if not db_model:
            return None
        return MLModel(
            id=db_model.id,
            name=db_model.name,
            description=db_model.description,
            cost=db_model.cost,
            type=db_model.type,
            model_name=db_model.model_name,
        )

    def _to_db_model(self, model: MLModel) -> MLModelDB:
        return MLModelDB(
            id=model.id,
            name=model.name,
            description=model.description,
            cost=model.cost,
            type=model.type,
            model_name=model.model_name,
        )

    async def add(self, model: MLModel) -> MLModel:
        """Adds a new model using the stored session."""
        db_model = self._to_db_model(model) 
        self.session.add(db_model)
        await self.session.flush()
        await self.session.refresh(db_model)
        return self._to_entity(db_model)

    async def get_by_id(self, model_id: uuid.UUID) -> Optional[MLModel]:
        """Gets a model by ID using the stored session."""
        stmt = select(MLModelDB).where(MLModelDB.id == model_id)
        result = await self.session.execute(stmt)
        db_model = result.scalar_one_or_none()
        return self._to_entity(db_model)

    async def get_by_name(self, name: str) -> Optional[MLModel]:
        """Gets a model by name using the stored session."""
        stmt = select(MLModelDB).where(MLModelDB.name == name)
        result = await self.session.execute(stmt)
        db_model = result.scalar_one_or_none()
        return self._to_entity(db_model)

    async def list_all(self) -> List[MLModel]:
        """Lists all models using the stored session."""
        stmt = select(MLModelDB).order_by(MLModelDB.name)
        result = await self.session.execute(stmt)
        db_models = result.scalars().all()
        return [self._to_entity(db_model) for db_model in db_models if db_model] # Add check