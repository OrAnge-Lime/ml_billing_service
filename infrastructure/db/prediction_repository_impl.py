import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession # Keep import here

from core.entities.prediction import Prediction
from core.repositories.prediction_repository import AbstractPredictionRepository
from .models import PredictionDB

class SQLAlchemyPredictionRepository(AbstractPredictionRepository):

    def __init__(self, session: AsyncSession):
        self.session = session # Store session injected via constructor

    def _to_entity(self, db_pred: PredictionDB) -> Prediction | None:
        if not db_pred:
            return None
        return Prediction(
            id=db_pred.id,
            user_id=db_pred.user_id,
            model_id=db_pred.model_id,
            input_data=db_pred.input_data,
            output_data=db_pred.output_data,
            timestamp=db_pred.timestamp,
            status=db_pred.status,
            cost_charged=db_pred.cost_charged,
            error_message=db_pred.error_message
        )

    def _to_db_model(self, prediction: Prediction) -> PredictionDB:
        return PredictionDB(
            id=prediction.id,
            user_id=prediction.user_id,
            model_id=prediction.model_id,
            input_data=prediction.input_data,
            output_data=prediction.output_data,
            timestamp=prediction.timestamp,
            status=prediction.status,
            cost_charged=prediction.cost_charged,
            error_message=prediction.error_message
        )

    async def add(self, prediction: Prediction) -> Prediction:
        """Adds a prediction record using the stored session."""
        db_pred = self._to_db_model(prediction)
        self.session.add(db_pred)
        await self.session.flush()
        # No refresh typically needed if entity default factory sets ID
        return prediction

    async def get_by_id(self, prediction_id: uuid.UUID) -> Optional[Prediction]:
        """Gets a prediction by ID using the stored session."""
        stmt = select(PredictionDB).where(PredictionDB.id == prediction_id)
        result = await self.session.execute(stmt)
        db_pred = result.scalar_one_or_none()
        return self._to_entity(db_pred)

    async def get_by_user_id(self, user_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List[Prediction]:
        """Gets predictions for a user using the stored session."""
        stmt = select(PredictionDB)\
            .where(PredictionDB.user_id == user_id)\
            .order_by(PredictionDB.timestamp.desc())\
            .limit(limit)\
            .offset(offset)
        result = await self.session.execute(stmt)
        db_preds = result.scalars().all()
        return [self._to_entity(db_pred) for db_pred in db_preds if db_pred] # Add check
