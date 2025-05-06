import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.use_cases.model_use_cases import (
    ModelUseCases,
)  # Import UseCase class if needed

from infrastructure.web.schemas import model_schemas
from infrastructure.web.dependencies.use_cases import get_model_use_case
from infrastructure.web.dependencies.auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/models",
    tags=["ML Models"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_model=List[model_schemas.MLModelRead])
async def list_available_models(
    model_use_cases: ModelUseCases = Depends(
        get_model_use_case
    ),  # Depend on use case provider
    # No session dependency
):
    """
    List all available ML models. Session managed via injected dependencies.
    """
    try:
        # Call use case method without session
        models = await model_use_cases.list_models()
        return models
    except Exception as e:
        logger.exception("Error listing models.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve models.",
        )


@router.get("/{model_id}", response_model=model_schemas.MLModelRead)
async def get_model_details(
    model_id: uuid.UUID,
    model_use_cases: ModelUseCases = Depends(
        get_model_use_case
    ),  # Depend on use case provider
    # No session dependency
):
    """
    Get details for a specific ML model. Session managed via injected dependencies.
    """
    try:
        # Call use case method without session
        model = await model_use_cases.get_model_details(model_id=model_id)
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
            )
        return model
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving details for model {model_id}.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model details.",
        )
