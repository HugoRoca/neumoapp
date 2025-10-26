from app.schemas.patient import PatientCreate, PatientLogin, PatientResponse, Token
from app.schemas.specialty import SpecialtyResponse, SpecialtyCreate
from app.schemas.hospital import HospitalResponse, HospitalCreate, HospitalUpdate, HospitalWithStats
from app.schemas.consultation_room import (
    ConsultationRoomCreate,
    ConsultationRoomUpdate,
    ConsultationRoomResponse,
    ConsultationRoomWithSpecialtiesResponse
)
from app.schemas.appointment import (
    AppointmentCreate, 
    AppointmentResponse, 
    AppointmentDetailResponse,
    AppointmentUpdate,
    TimeSlot,
    AvailableSlotsResponse,
    ConsultationRoomSimple
)

__all__ = [
    "PatientCreate",
    "PatientLogin",
    "PatientResponse",
    "Token",
    "SpecialtyResponse",
    "SpecialtyCreate",
    "HospitalResponse",
    "HospitalCreate",
    "HospitalUpdate",
    "HospitalWithStats",
    "ConsultationRoomCreate",
    "ConsultationRoomUpdate",
    "ConsultationRoomResponse",
    "ConsultationRoomWithSpecialtiesResponse",
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentDetailResponse",
    "AppointmentUpdate",
    "TimeSlot",
    "AvailableSlotsResponse",
    "ConsultationRoomSimple",
]
