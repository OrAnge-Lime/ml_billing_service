import datetime
import logging
import tempfile
import os
import shutil
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional

from contracts import ASRResponse, ErrorResponse, ASRModelCreate
from ml_models.model_registry import model_registry
from config import asr_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["asr"])


@router.post(
    "/models", summary="Add new ASR model"
)
async def add_new_model(
    model_params: ASRModelCreate  # TODO: return status code 201
):
    """
    Returns a list of available ASR models that this service supports.
    """
    try:
        await model_registry.add_model(model_params)
        logger.info(f"Load successful '{model_params.name}'.")

    except Exception as e:
        logger.exception(f"Unexpected error during loading model '{model_params.name}'")


# TODO: new data structure fot transcribe audio input
@router.post(
    "/transcribe",
    response_model=ASRResponse,
)
async def transcribe_audio(
    model_identifier: str = Form(
        ..., example="whisper-small", description="Identifier of the Whisper model."
    ),
    audio_file: UploadFile = File(..., description="The audio file to transcribe."),
    language: Optional[str] = Form(
        None,
        example="en",
        description="Optional: Language of the audio.",
    ),
    task: Optional[str] = Form(
        "transcribe",
        example="transcribe",
        description="Task to perform: 'transcribe' or 'translate'.",
    ),
):
    logger.info(
        f"Received /transcribe request for model: '{model_identifier}', file: '{audio_file.filename}'"
    )

    # Create a temporary directory to save the uploaded file safely
    temp_dir = tempfile.mkdtemp(prefix="asr_audio_")
    temp_file_path = os.path.join(temp_dir, audio_file.filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        logger.debug(
            f"Audio file '{audio_file.filename}' saved temporarily to '{temp_file_path}'"
        )

        model_instance = await model_registry.get_model(model_identifier)

        transcription_result = await model_instance.predict(
            audio_file_path=temp_file_path, language=language, task=task
        )
        logger.info(
            f"Transcription successful for '{audio_file.filename}' with model '{model_identifier}'."
        )

        return ASRResponse(
            model_identifier=model_identifier,
            transcribed_text=transcription_result.get("text", "No text transcribed."),
            language_detected=transcription_result.get("language_detected"),
            segments=transcription_result.get("segments"),
            processed_at=datetime.datetime.now(datetime.timezone.utc),
            status="success",
            message="Transcription successful.",
        )

    except Exception as e:
        logger.exception(
            f"Unexpected error during /transcribe for model '{model_identifier}'"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                message="An unexpected server error occurred.",
                model_identifier=model_identifier,
                error_type=e.__class__.__name__,
            ).model_dump(),
        )
    finally:
        if audio_file:
            await audio_file.close()
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e_cleanup:
                logger.error(
                    f"Error cleaning up temp directory {temp_dir}: {e_cleanup}"
                )
