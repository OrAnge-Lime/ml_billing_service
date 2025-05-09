import uuid
from typing import List, Optional
from ..entities.ml_model import MLModel
from ..repositories.ml_model_repository import AbstractMLModelRepository
from ..repositories.ml_model_repository import AbstractMLModelService



class ModelUseCases:
    def __init__(self, model_repo: AbstractMLModelRepository,
                 prediction_service: AbstractMLModelService):
        self.model_repo = model_repo
        self.prediction_service = prediction_service

    async def list_models(self) -> List[MLModel]:
        return await self.model_repo.list_all()

    async def get_model_details(self, model_id: uuid.UUID) -> Optional[MLModel]:
        return await self.model_repo.get_by_id(model_id)

    # Add use case for adding/registering models if needed (e.g., admin function)
    async def register_model(
        self,
        name: str,
        description: str,
        cost: int,
        type: str,
        model_name: str,
    ) -> MLModel:
        
        # Create model entity
        model = MLModel(
            name=name,
            description=description,
            cost=cost,
            type=type,
            model_name=model_name,
        )

        # TODO: Load model at ASR service as ASRModelCreate obj
        await self.prediction_service.upload_model(
                    name=name,
                    type=type,
                    model_name=model_name,
                )
        return await self.model_repo.add(model)
