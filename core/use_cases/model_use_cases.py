import uuid
from typing import List, Optional
from ..entities.ml_model import MLModel
from ..repositories.ml_model_repository import AbstractMLModelRepository

class ModelUseCases:
    def __init__(self, model_repo: AbstractMLModelRepository):
        self.model_repo = model_repo

    async def list_models(self) -> List[MLModel]:
        return await self.model_repo.list_all()

    async def get_model_details(self, model_id: uuid.UUID) -> Optional[MLModel]:
        return await self.model_repo.get_by_id(model_id)

    # Add use case for adding/registering models if needed (e.g., admin function)
    async def register_model(self, name: str, filename: str, description: str, cost: int) -> MLModel:
        model = MLModel(name=name, filename=filename, description=description, cost=cost)
        return await self.model_repo.add(model)
