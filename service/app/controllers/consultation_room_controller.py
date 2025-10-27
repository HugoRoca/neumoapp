from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.schemas.consultation_room import (
    ConsultationRoomCreate,
    ConsultationRoomUpdate,
    ConsultationRoomResponse,
    ConsultationRoomWithSpecialtiesResponse,
    AssignSpecialtyToRoomRequest,
    RemoveSpecialtyFromRoomRequest
)
from app.services.consultation_room_service import ConsultationRoomService
from app.core.dependencies import get_current_patient
from app.models.patient import Patient

router = APIRouter(prefix="/consultation-rooms", tags=["Consultation Rooms"])


@router.get("/", response_model=List[ConsultationRoomResponse])
async def list_consultation_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    List all active consultation rooms
    """
    service = ConsultationRoomService(db)
    return service.get_all_rooms(skip, limit)


@router.get("/by-specialty/{specialty_id}", response_model=List[ConsultationRoomResponse])
async def get_rooms_by_specialty(
    specialty_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Get consultation rooms assigned to a specific specialty
    
    Useful for checking which rooms are available for a specialty
    """
    service = ConsultationRoomService(db)
    return service.get_rooms_by_specialty(specialty_id)


@router.get("/by-hospital-and-specialty", response_model=List[ConsultationRoomResponse])
async def get_rooms_by_hospital_and_specialty(
    hospital_id: int,
    specialty_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Get consultation rooms for a specific hospital and specialty.
    
    **Use Case:**
    This endpoint is useful for the booking flow where a patient:
    1. Selects a hospital
    2. Selects a specialty
    3. Wants to see which consultation rooms are available
    
    **Parameters:**
    - **hospital_id** (query): Hospital ID
    - **specialty_id** (query): Specialty ID
    
    **Returns:**
    List of consultation rooms that:
    - Belong to the specified hospital
    - Are assigned to the specified specialty
    - Are active
    
    **Example:**
    ```
    GET /consultation-rooms/by-hospital-and-specialty?hospital_id=1&specialty_id=2
    ```
    """
    service = ConsultationRoomService(db)
    return service.get_rooms_by_hospital_and_specialty(hospital_id, specialty_id)


@router.get("/{room_id}", response_model=ConsultationRoomWithSpecialtiesResponse)
async def get_consultation_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Get consultation room details with assigned specialties"""
    service = ConsultationRoomService(db)
    room = service.get_room_by_id(room_id)
    
    # Format specialties for response
    specialties_data = [
        {"id": s.id, "name": s.name}
        for s in room.specialties
    ]
    
    # Create response dict
    response_data = {
        "id": room.id,
        "room_number": room.room_number,
        "name": room.name,
        "floor": room.floor,
        "building": room.building,
        "description": room.description,
        "active": room.active,
        "created_at": room.created_at,
        "updated_at": room.updated_at,
        "specialties": specialties_data
    }
    
    return response_data


@router.post("/", response_model=ConsultationRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_consultation_room(
    room: ConsultationRoomCreate,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Create a new consultation room (admin only)
    
    Can assign specialties during creation
    """
    service = ConsultationRoomService(db)
    return service.create_room(room)


@router.patch("/{room_id}", response_model=ConsultationRoomResponse)
async def update_consultation_room(
    room_id: int,
    room_update: ConsultationRoomUpdate,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Update consultation room (admin only)
    
    Can update specialty assignments
    """
    service = ConsultationRoomService(db)
    return service.update_room(room_id, room_update)


@router.post("/{room_id}/assign-specialty", response_model=ConsultationRoomResponse)
async def assign_specialty_to_room(
    room_id: int,
    request: AssignSpecialtyToRoomRequest,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Assign a specialty to a consultation room (admin only)
    """
    service = ConsultationRoomService(db)
    return service.assign_specialty(room_id, request.specialty_id)


@router.delete("/{room_id}/remove-specialty", response_model=ConsultationRoomResponse)
async def remove_specialty_from_room(
    room_id: int,
    request: RemoveSpecialtyFromRoomRequest,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Remove a specialty from a consultation room (admin only)
    """
    service = ConsultationRoomService(db)
    return service.remove_specialty(room_id, request.specialty_id)


@router.delete("/{room_id}", status_code=status.HTTP_200_OK)
async def deactivate_consultation_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Deactivate a consultation room (admin only)
    
    Soft delete - room remains in database but is inactive
    """
    service = ConsultationRoomService(db)
    service.deactivate_room(room_id)
    return {"message": "Consultation room deactivated successfully"}

