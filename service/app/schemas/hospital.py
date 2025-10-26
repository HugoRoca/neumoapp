"""
Hospital Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class HospitalBase(BaseModel):
    """Base schema for Hospital"""
    name: str
    code: str
    address: str
    district: Optional[str] = None
    city: str = "Lima"
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    active: bool = True


class HospitalCreate(HospitalBase):
    """Schema for creating a Hospital"""
    specialty_ids: Optional[List[int]] = Field(default=[], description="List of specialty IDs to assign to this hospital")


class HospitalUpdate(BaseModel):
    """Schema for updating a Hospital"""
    name: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class HospitalResponse(HospitalBase):
    """Schema for Hospital response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HospitalWithStats(HospitalResponse):
    """Schema for Hospital with statistics"""
    specialty_count: int = 0
    room_count: int = 0
    upcoming_appointments: int = 0
    
    class Config:
        from_attributes = True


# Specialty simple schema (para evitar importación circular)
class SpecialtySimple(BaseModel):
    """Simple specialty schema for nested responses"""
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class HospitalWithSpecialties(HospitalResponse):
    """Schema for Hospital with its specialties"""
    specialties: List[SpecialtySimple] = []
    
    class Config:
        from_attributes = True


class AssignSpecialtyRequest(BaseModel):
    """Schema for assigning a specialty to a hospital"""
    specialty_id: int = Field(..., description="Specialty ID to assign")


class RemoveSpecialtyRequest(BaseModel):
    """Schema for removing a specialty from a hospital"""
    specialty_id: int = Field(..., description="Specialty ID to remove")

