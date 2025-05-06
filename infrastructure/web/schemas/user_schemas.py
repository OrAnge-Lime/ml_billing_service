import uuid
from pydantic import BaseModel, Field, EmailStr

# Base model for common user fields
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")

# Schema for creating a new user (request)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="strongpassword")

# Schema for reading user data (response)
class UserRead(UserBase):
    id: uuid.UUID
    credits: int
    is_active: bool

    class Config:
        from_attributes = True # Updated from orm_mode=True for Pydantic v2
