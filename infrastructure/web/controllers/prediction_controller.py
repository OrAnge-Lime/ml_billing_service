import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from core.use_cases.prediction_use_cases import (
    PredictionUseCases,
    PredictionError,
    InsufficientCreditsError,
) 
from core.entities.user import User as UserEntity

from infrastructure.web.schemas import prediction_schemas
from infrastructure.web.dependencies.use_cases import get_prediction_use_case
from infrastructure.web.dependencies.auth import get_current_active_user

from infrastructure.db.user_repository_impl import SQLAlchemyUserRepository
from infrastructure.web.dependencies.db import (
    get_db_session,
)  #


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predict",
    tags=["Predictions"],
    dependencies=[Depends(get_current_active_user)],
)

@router.post("/{model_id}", response_model=prediction_schemas.PredictionResponse)
async def make_prediction(
    model_id: uuid.UUID,
    request_body: prediction_schemas.PredictionRequest,
    current_user: UserEntity = Depends(
        get_current_active_user
    ),  # Auth handled by dependency
    prediction_use_cases: PredictionUseCases = Depends(
        get_prediction_use_case
    ),  # Depend on use case provider
    # No session dependency needed here, transaction managed implicitly
):
    """
    Make a prediction. Session and transaction managed via injected dependencies.
    """
    try:
        # Call use case method without session
        result, prediction_id = await prediction_use_cases.make_prediction(
            user_id=current_user.id,
            model_id=model_id,
            input_data=request_body.input_data,
        )

        # To get updated credits, we need a UserUseCases instance
        # Option: Inject UserUseCases as well, or return credits from prediction use case
        # Let's inject UserUseCases for consistency (though feels slightly heavy)
        # Need to import get_user_use_case
        from infrastructure.web.dependencies.use_cases import get_user_use_case

        user_use_cases: UserUseCases = Depends(get_user_use_case)  # Inject this too

        # Fetch updated credits using the separate use case instance
        # Note: This uses the *same underlying session* because both use cases
        # ultimately depend on repositories derived from the same get_db_session call.
        updated_credits = await user_use_cases.check_user_credits(current_user.id)

        return prediction_schemas.PredictionResponse(
            prediction_id=prediction_id,
            model_id=model_id,
            result=result,
            credits_remaining=updated_credits,
        )
    except InsufficientCreditsError as e:
        logger.warning(
            f"Insufficient credits for user {current_user.id} on model {model_id}"
        )
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(e))
    except PredictionError as e:
        logger.warning(
            f"Prediction failed for user {current_user.id} on model {model_id}: {e}"
        )
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            # Includes model execution errors, etc.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(
            f"Unexpected error in prediction endpoint for user {current_user.id}, model {model_id}"
        )
        # The exception will trigger rollback via the get_db_session context manager
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during prediction.",
        )


@router.get("/history", response_model=List[prediction_schemas.PredictionRecord])
async def get_prediction_history(
    current_user: UserEntity = Depends(get_current_active_user),
    prediction_use_cases: PredictionUseCases = Depends(
        get_prediction_use_case
    ),  # Depend on use case provider
    limit: int = 100,
    offset: int = 0,
    # No session dependency
):
    """
    Get prediction history. Session managed via injected dependencies.
    """
    try:
        # Call use case method without session
        predictions = await prediction_use_cases.get_user_predictions(
            user_id=current_user.id, limit=limit, offset=offset
        )
        return predictions
    except Exception as e:
        logger.exception(
            f"Error retrieving prediction history for user {current_user.id}."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction history.",
        )
