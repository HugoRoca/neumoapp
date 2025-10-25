from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from app.schemas.patient import PatientResponse
from app.schemas.specialty import SpecialtyResponse


class ConsultationRoomSimple(BaseModel):
    """Simple consultation room info for slots"""
    id: int
    room_number: str
    name: str
    
    class Config:
        from_attributes = True


class TimeSlot(BaseModel):
    """Representa un slot de tiempo disponible"""
    start_time: time
    end_time: time
    consultation_room: ConsultationRoomSimple
    available: bool = True
    
    class Config:
        from_attributes = True


class AvailableSlotsResponse(BaseModel):
    """Respuesta con slots disponibles para una fecha y especialidad"""
    specialty_id: int
    specialty_name: str
    date: date
    shift: str
    slots: list[TimeSlot]


class AppointmentBase(BaseModel):
    specialty_id: int
    consultation_room_id: int = Field(..., description="Consultation room ID")
    appointment_date: date = Field(..., description="Appointment date (YYYY-MM-DD)")
    start_time: time = Field(..., description="Start time (HH:MM:SS)")
    shift: str = Field(..., description="Shift: morning or afternoon")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for appointment")


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Status: pending, confirmed, cancelled, completed")
    observations: Optional[str] = Field(None, max_length=500)


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    specialty_id: int
    consultation_room_id: int
    appointment_date: date
    start_time: time
    end_time: time
    shift: str
    status: str
    reason: Optional[str]
    observations: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentDetailResponse(AppointmentResponse):
    patient: PatientResponse
    specialty: SpecialtyResponse
    consultation_room: ConsultationRoomSimple

    class Config:
        from_attributes = True

