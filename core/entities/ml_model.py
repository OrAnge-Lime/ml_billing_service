import uuid
from dataclasses import dataclass, field
from typing import Optional

# @dataclass декоратор генерирует для класса специальные методы (вроде __init__, __repr__), делая код короче.
@dataclass
class MLModel:
    name: str
    filename: str 
    description: Optional[str] = None
    cost: int = 1 # Credits per prediction
    input_schema: Optional[dict] = None # Optional: Define expected input structure
    output_schema: Optional[dict] = None # Optional: Define expected output structure
    id: uuid.UUID = field(default_factory=uuid.uuid4) # dk_
