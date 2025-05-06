import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MLModelBase(BaseModel):
    name: str = Field(..., example="Iris Classifier KNN")
    filename: str = Field(..., example="iris_knn.joblib")
    description: Optional[str] = Field(None, example="KNN classifier for the Iris dataset")
    cost: int = Field(..., ge=0, example=1) # Credits per prediction, must be >= 0

    # Corrected examples: Use actual example values, not type objects
    input_schema: Optional[Dict[str, Any]] = Field(
        None,
        example={
            "description": "Expected input features and their types.",
            "type": "object",
            "properties": {
                "sepal_length": {"type": "number", "format": "float"},
                "sepal_width": {"type": "number", "format": "float"},
                "petal_length": {"type": "number", "format": "float"},
                "petal_width": {"type": "number", "format": "float"}
            },
            "required": ["sepal_length", "sepal_width", "petal_length", "petal_width"]
        }
        # Or a simpler example if you prefer just sample data:
        # example={"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
    )
    output_schema: Optional[Dict[str, Any]] = Field(
        None,
         example={
            "description": "Expected output format.",
            "type": "object",
            "properties": {
                "predicted_class": {"type": "integer", "description": "Predicted class index (e.g., 0, 1, 2)"}
            }
        }
        # Or a simpler example:
        # example={"predicted_class": 0}
    )


class MLModelRead(MLModelBase):
    id: uuid.UUID

    class Config:
        from_attributes = True # Use this instead of orm_mode for Pydantic v2+