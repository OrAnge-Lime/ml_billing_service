import uuid
from dataclasses import dataclass, field

@dataclass
class User:
    username: str
    hashed_password: str 
    credits: int = 0 # Default credits
    is_active: bool = True # Useful for soft deletes or disabling users
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    is_admin: bool = False
