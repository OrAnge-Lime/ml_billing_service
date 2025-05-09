import uuid
from dataclasses import dataclass, field
from typing import Optional


# @dataclass декоратор генерирует для класса специальные методы (вроде __init__, __repr__), делая код короче.
@dataclass
class MLModel:
    name: str
    model_name: str
    cost: int = 1  # Credits per prediction
    type: str = 'whisper'
    description: Optional[str] = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
