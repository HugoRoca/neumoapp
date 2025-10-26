from app.repositories.patient_repository import PatientRepository
from app.repositories.specialty_repository import SpecialtyRepository
from app.repositories.hospital_repository import HospitalRepository
from app.repositories.consultation_room_repository import ConsultationRoomRepository
from app.repositories.appointment_repository import AppointmentRepository

__all__ = [
    "PatientRepository",
    "SpecialtyRepository",
    "HospitalRepository",
    "ConsultationRoomRepository",
    "AppointmentRepository",
]
