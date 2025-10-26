from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SpecialtyBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None


class SpecialtyCreate(SpecialtyBase):
    pass


class SpecialtyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    active: Optional[bool] = None


class SpecialtyResponse(SpecialtyBase):
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Hospital simple schema (para evitar importación circular)
class HospitalSimple(BaseModel):
    """Simple hospital schema for nested responses"""
    id: int
    name: str
    code: str
    city: str
    
    class Config:
        from_attributes = True


class SpecialtyWithHospitals(SpecialtyResponse):
    """Schema for Specialty with its hospitals"""
    hospitals: List[HospitalSimple] = []
    available_rooms: int = 0  # Número de consultorios asignados a esta especialidad
    
    class Config:
        from_attributes = True


class SpecialtyWithRoomCount(SpecialtyResponse):
    """Schema for Specialty with room count for a specific hospital"""
    available_rooms: int = 0
    
    class Config:
        from_attributes = True

