import uuid
from pydantic import BaseModel, Field
from typing import Optional


class MLModelBase(BaseModel):
    name: str = Field(..., example="whisper-tiny")
    description: Optional[str] = Field(None, example="ASR Whisper model tiny")
    cost: int = Field(..., ge=0, example=1)


class ModelCreate(MLModelBase):
    type: str = "whisper"
    model_name: str = "tiny"


class MLModelRead(MLModelBase):
    id: uuid.UUID

    class Config:
        from_attributes = True  # Use this instead of orm_mode for Pydantic v2+
