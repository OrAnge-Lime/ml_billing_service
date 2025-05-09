from pydantic import BaseModel, Field
from dataclasses import field
from typing import Any, Optional, List, Dict # Added List, Dict
import datetime

class ASRResponse(BaseModel):
    """Response contract for the ASR service's transcribe endpoint."""
    model_identifier: str
    transcribed_text: str
    language_detected: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="List of transcribed segments with timestamps.")
    processed_at: datetime.datetime 
    status: str = "success"
    message: str = "Transcription successful."


class ErrorResponse(BaseModel):
    """Error response contract for the ASR service."""
    status: str = "error"
    message: str
    model_identifier: Optional[str] = None
    error_type: str = "TranscriptionError"


class ASRModelCreate(BaseModel):
    name: str = Field(..., example="whisper-tiny")
    type: str = "whisper"
    model_name: str = "tiny"
