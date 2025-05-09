import uuid
import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    credits = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_admin = Column(Boolean, default=False)

    predictions = relationship("PredictionDB", back_populates="user")


class MLModelDB(Base):
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    cost = Column(Integer, nullable=False, default=1)
    type = Column(Text, nullable=True)
    model_name = Column(Text, nullable=True)

    predictions = relationship("PredictionDB", back_populates="model")


class PredictionDB(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    model_name = Column(Text, ForeignKey("ml_models.name"), nullable=False)
    input_data = Column(JSON, nullable=False) # Store input features as JSON
    output_data = Column(JSON, nullable=True) # Store prediction output as JSON
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    status = Column(String, nullable=False, index=True) # 'success', 'failed'
    cost_charged = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)

    user = relationship("UserDB", back_populates="predictions")
    model = relationship("MLModelDB", back_populates="predictions")
