from app.services.auth_service import AuthService
from app.services.patient_service import PatientService
from app.services.specialty_service import SpecialtyService
from app.services.hospital_service import HospitalService
from app.services.consultation_room_service import ConsultationRoomService
from app.services.slot_service import SlotService
from app.services.appointment_service import AppointmentService

__all__ = [
    "AuthService",
    "PatientService",
    "SpecialtyService",
    "HospitalService",
    "ConsultationRoomService",
    "SlotService",
    "AppointmentService",
]
