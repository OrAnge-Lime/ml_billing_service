from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

# Import Base Interfaces (for type hinting)
from core.repositories.user_repository import AbstractUserRepository
from core.repositories.ml_model_repository import (
    AbstractMLModelRepository,
    AbstractMLModelService,
)
from core.repositories.prediction_repository import (
    AbstractPredictionRepository,
    AbstractPredictionService,
)

# Import Concrete Implementations
from infrastructure.db.user_repository_impl import SQLAlchemyUserRepository
from infrastructure.db.ml_model_repository_impl import SQLAlchemyMLModelRepository
from infrastructure.db.prediction_repository_impl import SQLAlchemyPredictionRepository

from infrastructure.web.prediction_service_impl import HttpServicePrediction, HttpServiceMLModel
from config.settings import settings
from .ml_model import get_asr_http_client

# Import session dependency
from .db import get_db_session

# Dependency functions to provide repository instances with injected session


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractUserRepository:
    """Provides a user repository instance scoped to the request session."""
    return SQLAlchemyUserRepository(session=session)


def get_ml_model_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractMLModelRepository:
    """Provides an ML model repository instance scoped to the request session."""
    return SQLAlchemyMLModelRepository(session=session)


def get_prediction_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AbstractPredictionRepository:
    """Provides a prediction repository instance scoped to the request session."""
    return SQLAlchemyPredictionRepository(session=session)


def get_prediction_service(
    http_client: httpx.AsyncClient = Depends(get_asr_http_client),
) -> AbstractPredictionService:
    return HttpServicePrediction(settings.ASR_SERVICE_URL + "/transcribe", http_client)


def get_ml_model_service(
    http_client: httpx.AsyncClient = Depends(get_asr_http_client),
) -> AbstractMLModelService:
    return HttpServiceMLModel(settings.ASR_SERVICE_URL + "/models", http_client)
