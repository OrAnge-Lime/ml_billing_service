import uuid
import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

# Schema for making a prediction request
class PredictionRequest(BaseModel):
    # Define the expected structure of input data
    # Using a simple dict here, but could be more specific
    # e.g., using List[float] or a nested Pydantic model
    input_data: Dict[str, Any] | list = Field(..., example={"feature1": 1.0, "feature2": 2.5} ) # Or example=[[1.0, 2.5]]

# Schema for the prediction response (successful)
class PredictionResponse(BaseModel):
    prediction_id: uuid.UUID
    model_id: uuid.UUID
    result: Any = Field(..., example=[0] or {"class": "setosa"}) # Example output
    credits_remaining: int

# Schema for reading past prediction records
class PredictionRecord(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    model_id: uuid.UUID
    input_data: Dict[str, Any] | list
    output_data: Optional[Any] = None
    timestamp: datetime.datetime
    status: str
    cost_charged: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
