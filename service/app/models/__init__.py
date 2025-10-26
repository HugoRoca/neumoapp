from app.models.patient import Patient
from app.models.specialty import Specialty
from app.models.hospital import Hospital
from app.models.consultation_room import ConsultationRoom, specialty_rooms
from app.models.appointment import Appointment, AppointmentStatus, ShiftType

__all__ = [
    "Patient", 
    "Specialty",
    "Hospital",
    "ConsultationRoom",
    "specialty_rooms",
    "Appointment", 
    "AppointmentStatus", 
    "ShiftType"
]
