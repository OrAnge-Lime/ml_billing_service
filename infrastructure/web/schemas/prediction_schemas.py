import uuid
import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List


class PredictionRequest(BaseModel):
    """
    Schema for data to be logged for a prediction request.
    The actual audio is sent as a file upload, not in this JSON body.
    This schema can hold metadata about the audio.
    """

    original_filename: Optional[str] = Field(None, example="meeting_audio.mp3")
    content_type: Optional[str] = Field(None, example="audio/mpeg")
    size_bytes: Optional[int] = Field(None, example=1024000)
    asr_language_param: Optional[str] = Field(
        None, example="en", description="Language hint passed to ASR."
    )
    asr_task_param: Optional[str] = Field(
        None,
        example="transcribe",
        description="Task (transcribe/translate) passed to ASR.",
    )


class PredictionResponse(BaseModel):
    """Response from the main API after a prediction (transcription) attempt."""

    prediction_id: uuid.UUID
    model_name: str
    result: Optional[str] = Field(None, description="Transcribed text")
    status_of_prediction: str = Field(
        ..., description="Status of the prediction attempt ('success' or 'failed')."
    )
    credits_remaining: int
    message: Optional[str] = Field(
        None, description="Additional message, e.g., error details."
    )


class PredictionRecord(BaseModel):  # For retrieving history
    id: uuid.UUID
    user_id: uuid.UUID
    model_name: str  # Refers to MLModelDB entry
    input_data: Dict[str, Any]  # Stores metadata like filename, size, content_type
    output_data: Optional[str] = None  # Transcribed text
    timestamp: datetime.datetime
    status: str  # 'success' or 'failed'
    cost_charged: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
