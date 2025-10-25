from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConsultationRoomBase(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=20, description="Room number or code (e.g., '101', 'A-1')")
    name: str = Field(..., min_length=3, max_length=100, description="Room name")
    floor: Optional[str] = Field(None, max_length=20, description="Floor number or level")
    building: Optional[str] = Field(None, max_length=50, description="Building name")
    description: Optional[str] = Field(None, max_length=255)


class ConsultationRoomCreate(ConsultationRoomBase):
    specialty_ids: List[int] = Field(default=[], description="List of specialty IDs to assign to this room")


class ConsultationRoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    floor: Optional[str] = Field(None, max_length=20)
    building: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    active: Optional[bool] = None
    specialty_ids: Optional[List[int]] = Field(None, description="Update specialty assignments")


class ConsultationRoomResponse(ConsultationRoomBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConsultationRoomWithSpecialtiesResponse(ConsultationRoomResponse):
    """Response with assigned specialties"""
    specialties: List[dict] = []  # List of {"id": int, "name": str}

    class Config:
        from_attributes = True


class AssignSpecialtyToRoomRequest(BaseModel):
    specialty_id: int = Field(..., description="Specialty ID to assign")


class RemoveSpecialtyFromRoomRequest(BaseModel):
    specialty_id: int = Field(..., description="Specialty ID to remove")

