from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate, AppointmentDetailResponse
from app.services.appointment_service import AppointmentService
from app.core.dependencies import get_current_patient
from app.models.patient import Patient

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Book a new medical appointment
    
    **Required fields:**
    - **specialty_id**: Medical specialty ID
    - **consultation_room_id**: Consultation room ID
    - **appointment_date**: Appointment date (YYYY-MM-DD)
    - **start_time**: Start time (HH:MM:SS)
    - **shift**: Shift type (morning or afternoon)
    - **reason**: Reason for consultation (optional)
    
    **Important:**
    - Use GET /slots/available to see available slots first
    - Appointments are 20 minutes long
    - Only weekdays (Monday-Friday)
    - Morning: 8:00 AM - 1:00 PM
    - Afternoon: 2:00 PM - 6:00 PM
    """
    service = AppointmentService(db)
    return service.book_appointment(appointment, current_patient)


@router.get("/my-appointments", response_model=List[AppointmentDetailResponse])
async def get_my_appointments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Get all appointments for authenticated patient (Dashboard)
    
    Returns appointments ordered by date and time (most recent first)
    Includes full details: patient, specialty, date, time, room, status
    """
    service = AppointmentService(db)
    return service.get_my_appointments(current_patient, skip, limit)


@router.get("/upcoming", response_model=List[AppointmentDetailResponse])
async def get_upcoming_appointments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Get upcoming appointments for authenticated patient
    
    Returns only future appointments (from today onwards)
    Status: pending or confirmed
    Ordered by date and time (nearest first)
    """
    service = AppointmentService(db)
    return service.get_upcoming_appointments(current_patient, skip, limit)


@router.get("/{appointment_id}", response_model=AppointmentDetailResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Get appointment details by ID"""
    service = AppointmentService(db)
    return service.get_appointment_by_id(appointment_id, current_patient)


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Update appointment status or observations
    
    - **status**: pending, confirmed, rescheduled, cancelled, completed
    - **observations**: Additional notes
    """
    service = AppointmentService(db)
    return service.update_appointment(appointment_id, appointment_update, current_patient)


@router.delete("/{appointment_id}", status_code=status.HTTP_200_OK)
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Cancel an appointment
    
    The time slot becomes available again automatically
    Only pending or confirmed appointments can be cancelled
    """
    service = AppointmentService(db)
    return service.cancel_appointment(appointment_id, current_patient)
