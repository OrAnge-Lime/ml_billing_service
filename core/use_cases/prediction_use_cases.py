import uuid
import datetime
from typing import Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession # Import Session for transaction management

from ..entities.prediction import Prediction
from ..repositories.user_repository import AbstractUserRepository
from ..repositories.ml_model_repository import AbstractMLModelRepository
from ..repositories.prediction_repository import AbstractPredictionRepository
from infrastructure.ml.model_loader import ModelLoader, ModelExecutionError # Specific loader/error
from config.settings import settings # Access settings for model directory

class PredictionError(Exception):
    """Custom exception for prediction failures."""
    pass

class InsufficientCreditsError(PredictionError):
    """Custom exception for insufficient credits."""
    pass


class PredictionUseCases:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        model_repo: AbstractMLModelRepository,
        prediction_repo: AbstractPredictionRepository,
        model_loader: ModelLoader # Inject the model loader
    ):
        self.user_repo = user_repo
        self.model_repo = model_repo
        self.prediction_repo = prediction_repo
        self.model_loader = model_loader

    async def make_prediction(
        self,
        user_id: uuid.UUID,
        model_id: uuid.UUID,
        input_data: dict,
        db_session: AsyncSession
    ) -> Tuple[Any, uuid.UUID]:
        """
        Makes a prediction, handles billing, and records the transaction.
        Returns the prediction output and the prediction record ID.
        Raises PredictionError or InsufficientCreditsError on failure.
        """
        async with db_session.begin():
            # Fetch User and Model (lock user row for update) dk_
            # Use with_for_update to lock the user row during the transaction
            user = await self.user_repo.get_by_id_for_update(user_id, db_session) # Modify repo interface/impl
            model = await self.model_repo.get_by_id(model_id) # No lock needed for model typically

            if not user:
                raise PredictionError(f"User id {user_id} not found.")
            if not user.is_active:
                 raise PredictionError(f"User {user.username} is not active.")
            if not model:
                raise PredictionError(f"Model id {model_id} not found.")

            # Check Credits
            if user.credits < model.cost:
                raise InsufficientCreditsError(
                    f"Insufficient credits. Required: {model.cost}, Available: {user.credits}"
                )

            # Load and Execute Model
            prediction_output = None
            error_message = None
            status = 'pending'
            cost_charged = 0

            try:
                prediction_output = await self.model_loader.predict(model.filename, input_data)
                status = 'success'

            except ModelExecutionError as e:
                status = 'failed'
                error_message = f"Model execution failed: {str(e)}"

            except Exception as e:
                # unexpected errors
                status = 'failed'
                error_message = f"Unexpected prediction error: {str(e)}"

            # Record Prediction 
            prediction_record = Prediction(
                user_id=user.id,
                model_id=model.id,
                input_data=input_data, # Ensure input_data is serializable (e.g., dict)
                output_data=prediction_output, # Ensure output is serializable
                timestamp=datetime.datetime.utcnow(),
                status=status,
                cost_charged=cost_charged,
                error_message=error_message
            )
            # Use the session directly for adding within the transaction
            await self.prediction_repo.add_with_session(prediction_record, db_session) # Modify repo interface/impl dk_

            # Upd credits 
            if status == 'success':
                new_balance = user.credits - model.cost
                # Use the session directly for updating within the transaction
                await self.user_repo.update_credits_with_session(user.id, new_balance, db_session) # Modify repo interface/impl

        # Return result only if successful, otherwise exceptions are raised
        if status == 'success':
            return prediction_output, prediction_record.id
        else:
            raise PredictionError(error_message or "Prediction failed for an unknown reason.") # dk_


    async def get_user_predictions(self, user_id: uuid.UUID, limit: int = 10, offset: int = 0) -> List[Prediction]:
         return await self.prediction_repo.get_by_user_id(user_id, limit=limit, offset=offset)