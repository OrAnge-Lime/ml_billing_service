from fastapi import Depends

# Import Use Case classes
from core.use_cases.user_use_cases import UserUseCases
from core.use_cases.model_use_cases import ModelUseCases
from core.use_cases.prediction_use_cases import PredictionUseCases

# Import Repository Interfaces (type hints) / Dependencies
from core.repositories.user_repository import AbstractUserRepository
from core.repositories.ml_model_repository import AbstractMLModelRepository
from core.repositories.prediction_repository import AbstractPredictionRepository
from .repositories import (
    get_user_repository,
    get_ml_model_repository,
    get_prediction_repository
)

# Import Model Loader instance (infrastructure detail needed by PredictionUseCases)
from infrastructure.ml.model_loader import model_loader

# Dependency functions to provide use case instances with injected repositories

def get_user_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository)
) -> UserUseCases:
    """Provides a UserUseCases instance with its dependencies."""
    return UserUseCases(user_repo=user_repo)

def get_model_use_case(
    model_repo: AbstractMLModelRepository = Depends(get_ml_model_repository)
) -> ModelUseCases:
    """Provides a ModelUseCases instance with its dependencies."""
    return ModelUseCases(model_repo=model_repo)

def get_prediction_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repository),
    model_repo: AbstractMLModelRepository = Depends(get_ml_model_repository),
    prediction_repo: AbstractPredictionRepository = Depends(get_prediction_repository)
    # Note: ModelLoader is a singleton, typically not request-scoped, injected directly
) -> PredictionUseCases:
    """Provides a PredictionUseCases instance with its dependencies."""
    return PredictionUseCases(
        user_repo=user_repo,
        model_repo=model_repo,
        prediction_repo=prediction_repo,
        model_loader=model_loader # Inject the singleton loader
    )
