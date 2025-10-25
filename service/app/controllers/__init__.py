from app.controllers.auth_controller import router as auth_router
from app.controllers.patient_controller import router as patient_router
from app.controllers.specialty_controller import router as specialty_router
from app.controllers.consultation_room_controller import router as consultation_room_router
from app.controllers.slot_controller import router as slot_router
from app.controllers.appointment_controller import router as appointment_router

__all__ = [
    "auth_router",
    "patient_router",
    "specialty_router",
    "consultation_room_router",
    "slot_router",
    "appointment_router",
]
