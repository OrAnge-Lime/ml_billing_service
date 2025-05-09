import uuid
import datetime
import logging
from typing import Tuple, List, Optional # Added Optional
import io

from ..entities.prediction import Prediction
from ..repositories.user_repository import AbstractUserRepository
from ..repositories.ml_model_repository import AbstractMLModelRepository
from ..repositories.prediction_repository import AbstractPredictionRepository, AbstractPredictionService

logger = logging.getLogger(__name__)


class PredictionUseCases:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        model_repo: AbstractMLModelRepository,
        prediction_repo: AbstractPredictionRepository,
        prediction_service: AbstractPredictionService
    ):
        self.user_repo = user_repo
        self.model_repo = model_repo
        self.prediction_repo = prediction_repo
        self.prediction_service = prediction_service

    async def make_prediction(
        self,
        user_id: uuid.UUID,
        model_name: str,
        audio_file_content: bytes,
        audio_filename: str,
        audio_content_type: str,
        asr_language_param: Optional[str]=None,
        asr_task_param: Optional[str]=None
    ) -> Tuple[Optional[str], uuid.UUID, str, str]: # (transcribed_text, prediction_db_id, model_identifier_str, status_str)

        final_status_str = 'pending'
        cost_charged = 0
        error_message = None
        transcribed_text_from_asr = None
        prediction_db_id = None


        # Logged input data for PredictionDB
        logged_input_metadata = {
            "original_filename": audio_filename,
            "content_type": audio_content_type,
            "size_bytes": len(audio_file_content),
            "asr_language_param": asr_language_param,
            "asr_task_param": asr_task_param,
        }

        try:
            # Fetch user and DB model entry
            user = await self.user_repo.get_by_id_for_update(user_id)
            db_model_entry = await self.model_repo.get_by_name(model_name)
            logged_input_metadata["requested_model_name"] = model_name

            # Check Credits
            if user.credits < db_model_entry.cost:
                raise Exception(f"Insufficient credits. Required: {db_model_entry.cost}, Current: {user.credits}")

            # Call External ASR Service
            try:
                asr_response_data = await self.prediction_service.get_prediction(
                    model_name=model_name,
                    file=io.BytesIO(audio_file_content), # TODO: dataclass
                    lang=asr_language_param,
                    task=asr_task_param,
                )
                logger.debug(f"ASR service response data: {asr_response_data}")

                if asr_response_data.get("status") == "success":
                    transcribed_text_from_asr = asr_response_data.get("transcribed_text")
                    final_status_str = 'success'
                    cost_charged = db_model_entry.cost 
                else:
                    final_status_str = 'failed'
                    error_message = asr_response_data.get("message", "ASR service indicated failure without details.")
                    logger.error(f"ASR service failed for {model_name}: {error_message}")

            except Exception as e:
                logger.exception(f"Unexpected error calling ASR for {model_name}")

            # Record Prediction Attempt
            prediction_to_save = Prediction(
                user_id=user.id,
                model_name=db_model_entry.name,
                input_data=logged_input_metadata,
                output_data=transcribed_text_from_asr,
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                status=final_status_str,
                cost_charged=cost_charged,
                error_message=error_message
            )
            saved_prediction = await self.prediction_repo.add(prediction_to_save)
            prediction_db_id = saved_prediction.id

            # Deduct Credits
            if final_status_str == 'success':
                await self.user_repo.update_credits(user.id, user.credits - cost_charged)
                return transcribed_text_from_asr, prediction_db_id, model_name, final_status_str
            else:
                raise Exception(error_message or "ASR processing failed for an unknown reason.")

        except Exception as e:
            logger.warning(f"Prediction error for user {user_id}: {e}")
            raise e 


    async def get_user_predictions(
        self, user_id: uuid.UUID, limit: int = 10, offset: int = 0
    ) -> List[Prediction]:
        return await self.prediction_repo.get_by_user_id(user_id, limit=limit, offset=offset)