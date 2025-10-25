from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SpecialtyBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    consultation_rooms: int = Field(default=1, ge=1, le=20, description="Number of consultation rooms available")


class SpecialtyCreate(SpecialtyBase):
    pass


class SpecialtyResponse(SpecialtyBase):
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True

