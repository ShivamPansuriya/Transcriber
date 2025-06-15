from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class TranscriptionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionRequest(BaseModel):
    language: Optional[str] = None  # Auto-detect if None
    
class TranscriptionResponse(BaseModel):
    id: int
    status: TranscriptionStatus
    message: str
    created_at: datetime
    
class TranscriptionResult(BaseModel):
    id: int
    status: TranscriptionStatus
    text: Optional[str] = None
    language: Optional[str] = None
    duration: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ErrorResponse(BaseModel):
    id: int = 0
    error: str
    message: str
