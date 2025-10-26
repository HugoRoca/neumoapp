"""
Hospital Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
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
    pass


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
    total_rooms: int = 0
    total_specialties: int = 0
    total_appointments: int = 0
    
    class Config:
        from_attributes = True

