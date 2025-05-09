import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Path

from core.use_cases.prediction_use_cases import PredictionUseCases
from core.use_cases.user_use_cases import UserUseCases
from core.use_cases.model_use_cases import ModelUseCases # For fetching model identifier string
from core.entities.user import User as UserEntity
from infrastructure.web.schemas import prediction_schemas
from infrastructure.web.dependencies.use_cases import get_prediction_use_case, get_user_use_case, get_model_use_case
from infrastructure.web.dependencies.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Predictions"], dependencies=[Depends(get_current_active_user)])


# TODO: fit PredictionRequest
@router.post(
    "/{db_model}/transcribe", # db_model is the UUID of the MLModelDB entry
    response_model=prediction_schemas.PredictionResponse,
    description="Transcribe Audio File"
)
async def transcribe_audio_with_model(
    db_model: str,
    audio_file: UploadFile = File(..., description="The input audio file."),
    language: Optional[str] = Form(None, example="en", description="Optional: Target language code for transcription"),
    task: Optional[str] = Form("transcribe", example="transcribe", description="ASR task: 'transcribe' or 'translate' (to English)."),
    current_user: UserEntity = Depends(get_current_active_user),
    prediction_use_cases: PredictionUseCases = Depends(get_prediction_use_case),
    user_use_cases: UserUseCases = Depends(get_user_use_case),
):
    logger.info(f"Controller: ASR request for db_model '{db_model}' by user '{current_user.username}' with file '{audio_file.filename}'")

    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        logger.warning(f"Invalid file type '{audio_file.content_type}' from user '{current_user.username}'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Please upload an audio file (e.g., mp3, wav, m4a).")

    try:
        audio_content = await audio_file.read()
        if not audio_content:
            logger.warning(f"Empty audio file uploaded by user '{current_user.username}'")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio file cannot be empty.")

        transcribed_text, prediction_db_id, model_identifier_used_str, final_status = await prediction_use_cases.make_prediction(
            user_id=current_user.id,
            model_name=db_model,
            audio_file_content=audio_content,
            audio_filename=audio_file.filename or "uploaded_audio", # Ensure filename is not None
            audio_content_type=audio_file.content_type,
            asr_language_param=language,
            asr_task_param=task
        )

        updated_credits = await user_use_cases.check_user_credits(current_user.id)

        # In prediction_schemas.PredictionResponse, result is Optional[str]
        # model_identifier_used is returned by use_case
        response_payload = prediction_schemas.PredictionResponse(
            prediction_id=prediction_db_id,
            model_name=db_model,
            result=transcribed_text, # This will be None if final_status is 'failed'
            status_of_prediction=final_status,
            credits_remaining=updated_credits,
            message="Transcription successful." if final_status == "success" else "Transcription failed. See logs for details."
        )
        # If the process failed, the use case should have raised an error.
        # If it returns normally but status is 'failed', that's an unexpected state.
        if final_status != "success" and transcribed_text is not None: # Should not happen
             logger.error("Use case returned success text with failed status. Inconsistency.")
        # The client will see 200 OK, but status_of_prediction in payload tells them the outcome.
        # If an exception was raised, it would be caught by handlers below.
        return response_payload

    except Exception as e:
        logger.exception(f"Unexpected controller error for user '{current_user.username}', model '{db_model}'")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected internal server error occurred.")
    finally:
        if audio_file: # Ensure file is closed
            await audio_file.close()


# get_prediction_history endpoint remains the same
@router.get("/history", response_model=List[prediction_schemas.PredictionRecord])
async def get_prediction_history(
    current_user: UserEntity = Depends(get_current_active_user),
    prediction_use_cases: PredictionUseCases = Depends(get_prediction_use_case),
    limit: int = 100,
    offset: int = 0
):
    try:
        predictions = await prediction_use_cases.get_user_predictions(
            user_id=current_user.id, limit=limit, offset=offset
        )
        return predictions
    except Exception as e:
        logger.exception(f"Error retrieving prediction history for user {current_user.id}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve prediction history.")