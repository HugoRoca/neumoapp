from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database.base import get_db
from app.schemas.appointment import AvailableSlotsResponse
from app.services.slot_service import SlotService
from app.core.dependencies import get_current_patient
from app.models.patient import Patient

router = APIRouter(prefix="/slots", tags=["Available Slots"])


@router.get("/available", response_model=AvailableSlotsResponse)
async def get_available_slots(
    hospital_id: int = Query(..., description="Hospital ID"),
    specialty_id: int = Query(..., description="Specialty ID"),
    date: date = Query(..., description="Date to check availability (YYYY-MM-DD)"),
    shift: str = Query(..., description="Shift: morning or afternoon"),
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Get available time slots for booking appointments.
    
    **Booking Flow (Step 3):**
    1. GET /hospitals → Select a hospital
    2. GET /hospitals/{hospital_id}/specialties → Select a specialty
    3. **GET /slots/available** → Check available time slots (you are here)
    4. POST /appointments → Book the appointment
    
    **Parameters:**
    - **hospital_id**: Hospital ID where the appointment will take place
    - **specialty_id**: Medical specialty ID (must be offered by the hospital)
    - **date**: Date for the appointment (format: YYYY-MM-DD)
    - **shift**: Shift type (morning: 8AM-1PM, afternoon: 2PM-6PM)
    
    **Returns:**
    - List of available slots (20-minute intervals)
    - Each slot shows start_time, end_time, and consultation_room
    - Only slots from consultation rooms that:
      * Belong to the selected hospital
      * Are assigned to the selected specialty
      * Are not already booked
    
    **Business Rules:**
    - Only weekdays (Monday-Friday)
    - Only future times if date is today
    - Morning shift: 8:00 AM - 1:00 PM
    - Afternoon shift: 2:00 PM - 6:00 PM
    - Duration: 20 minutes per appointment
    """
    service = SlotService(db)
    return service.get_available_slots(hospital_id, specialty_id, date, shift)

