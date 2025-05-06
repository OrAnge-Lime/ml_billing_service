import abc
import uuid
from typing import Optional, List
from ..entities.ml_model import MLModel

class AbstractMLModelRepository(abc.ABC):
    @abc.abstractmethod # метод нельзя использовать напрямую; нужно создать конкретную реализацию
    async def add(self, model: MLModel) -> MLModel:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, model_id: uuid.UUID) -> Optional[MLModel]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_name(self, name: str) -> Optional[MLModel]:
        raise NotImplementedError

    @abc.abstractmethod
    async def list_all(self) -> List[MLModel]:
        raise NotImplementedError
