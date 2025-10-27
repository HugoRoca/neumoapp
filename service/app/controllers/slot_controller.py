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
    room_id: int = Query(None, description="Optional: Filter by specific consultation room ID"),
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Get all time slots (available and occupied) for booking appointments.
    
    **Booking Flow (Step 3):**
    1. GET /hospitals → Select a hospital
    2. GET /hospitals/{hospital_id}/specialties → Select a specialty
    3. **GET /slots/available** → Check time slots (you are here)
    4. POST /appointments → Book the appointment
    
    **Parameters:**
    - **hospital_id**: Hospital ID where the appointment will take place
    - **specialty_id**: Medical specialty ID (must be offered by the hospital)
    - **date**: Date for the appointment (format: YYYY-MM-DD)
    - **shift**: Shift type (morning: 8AM-1PM, afternoon: 2PM-6PM)
    - **room_id** (optional): Consultation room ID to filter slots by specific room
    
    **Returns:**
    - List of ALL slots (20-minute intervals) for the specified parameters
    - Each slot includes:
      * `start_time`: Start time of the slot
      * `end_time`: End time of the slot
      * `consultation_room`: Room details (id, room_number, name)
      * `available`: **true** if slot is free, **false** if already booked
    - Slots are from consultation rooms that:
      * Belong to the selected hospital
      * Are assigned to the selected specialty
      * Match the room_id (if provided)
    
    **Business Rules:**
    - Only weekdays (Monday-Friday)
    - Only future times if date is today
    - Morning shift: 8:00 AM - 1:00 PM
    - Afternoon shift: 2:00 PM - 6:00 PM
    - Duration: 20 minutes per appointment
    
    **Examples:**
    - Get all slots: `?hospital_id=1&specialty_id=2&date=2024-10-28&shift=morning`
    - Get slots for specific room: `?hospital_id=1&specialty_id=2&date=2024-10-28&shift=morning&room_id=4`
    """
    service = SlotService(db)
    return service.get_available_slots(hospital_id, specialty_id, date, shift, room_id)

