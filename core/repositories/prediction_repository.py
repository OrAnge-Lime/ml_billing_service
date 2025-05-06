import abc
import uuid
from typing import List, Optional
from ..entities.prediction import Prediction

class AbstractPredictionRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, prediction: Prediction) -> Prediction:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, prediction_id: uuid.UUID) -> Optional[Prediction]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List[Prediction]:
        raise NotImplementedError
