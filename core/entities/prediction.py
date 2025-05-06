import uuid
import datetime
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Prediction:
    user_id: uuid.UUID
    model_id: uuid.UUID
    input_data: dict # Store input as JSON/dict
    status: str # 'pending', 'success', 'failed'
    output_data: Optional[Any] = None # Store output (can be complex)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow) # dk_
    cost_charged: int = 0
    error_message: Optional[str] = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
