from fastapi import Depends
import httpx

from core.use_cases.user_use_cases import UserUseCases
from core.use_cases.model_use_cases import ModelUseCases
from core.use_cases.prediction_use_cases import PredictionUseCases

from core.repositories.user_repository import AbstractUserRepository
from core.repositories.ml_model_repository import AbstractMLModelRepository, AbstractMLModelService
from core.repositories.prediction_repository import AbstractPredictionRepository, AbstractPredictionService
from .repositories import (
    get_user_repository,
    get_ml_model_repository,
    get_prediction_repository,
    get_prediction_service,
    get_ml_model_service
)

def get_user_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository)
) -> UserUseCases:
    return UserUseCases(user_repo=user_repo)

def get_model_use_case(
    model_repo: AbstractMLModelRepository = Depends(get_ml_model_repository),
    prediction_service: AbstractMLModelService = Depends(get_ml_model_service) # Use ASR client
) -> ModelUseCases:
    return ModelUseCases(model_repo=model_repo, prediction_service=prediction_service)

def get_prediction_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository),
    model_repo: AbstractMLModelRepository = Depends(get_ml_model_repository),
    prediction_repo: AbstractPredictionRepository = Depends(get_prediction_repository),
    prediction_service: AbstractPredictionService = Depends(get_prediction_service) # Use ASR client
) -> PredictionUseCases:
    return PredictionUseCases(
        user_repo=user_repo,
        model_repo=model_repo,
        prediction_repo=prediction_repo,
        prediction_service=prediction_service
    )