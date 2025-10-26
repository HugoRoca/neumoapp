"""
Hospital Controller
Handles HTTP requests for hospitals
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.schemas.hospital import (
    HospitalResponse, 
    HospitalCreate, 
    HospitalUpdate, 
    HospitalWithSpecialties,
    AssignSpecialtyRequest,
    RemoveSpecialtyRequest
)
from app.schemas.specialty import SpecialtyWithRoomCount
from app.repositories.hospital_repository import HospitalRepository
from app.repositories.specialty_repository import SpecialtyRepository
from app.services.hospital_service import HospitalService
from app.models.patient import Patient
from app.core.dependencies import get_current_patient

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.get("/", response_model=List[HospitalResponse])
def get_hospitals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Get all active hospitals.
    
    This endpoint returns a list of all hospitals where patients can book appointments.
    """
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    service = HospitalService(repository, specialty_repo)
    return service.get_all_hospitals(skip=skip, limit=limit)


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Get a specific hospital by ID"""
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    service = HospitalService(repository, specialty_repo)
    return service.get_hospital_by_id(hospital_id)


@router.get("/{hospital_id}/with-specialties", response_model=HospitalWithSpecialties)
def get_hospital_with_specialties(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Get hospital details with all its specialties"""
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    service = HospitalService(repository, specialty_repo)
    return service.get_hospital_with_specialties(hospital_id)


@router.get("/{hospital_id}/specialties", response_model=List[SpecialtyWithRoomCount])
def get_hospital_specialties(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Get all specialties available at a specific hospital.
    
    This is the **first step** in the booking flow:
    1. Patient selects a hospital
    2. This endpoint returns available specialties at that hospital
    3. Patient selects a specialty
    4. Patient checks available slots
    5. Patient books an appointment
    """
    from app.repositories.consultation_room_repository import ConsultationRoomRepository
    
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    room_repo = ConsultationRoomRepository(db)
    service = HospitalService(repository, specialty_repo)
    
    specialties = service.get_hospital_specialties(hospital_id)
    
    # Enrich with room count
    result = []
    for specialty in specialties:
        rooms = room_repo.get_by_hospital_and_specialty(hospital_id, specialty.id)
        result.append(SpecialtyWithRoomCount(
            **specialty.__dict__,
            available_rooms=len(rooms)
        ))
    
    return result


@router.post("/", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
def create_hospital(
    hospital: HospitalCreate,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Create a new hospital (Admin only)"""
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    service = HospitalService(repository, specialty_repo)
    return service.create_hospital(hospital)


@router.patch("/{hospital_id}", response_model=HospitalResponse)
def update_hospital(
    hospital_id: int,
    hospital: HospitalUpdate,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Update hospital (Admin only)"""
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    service = HospitalService(repository, specialty_repo)
    return service.update_hospital(hospital_id, hospital)


@router.delete("/{hospital_id}", status_code=status.HTTP_200_OK)
def deactivate_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Deactivate hospital (Admin only)"""
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    service = HospitalService(repository, specialty_repo)
    return service.deactivate_hospital(hospital_id)


# Specialty management endpoints

@router.post("/{hospital_id}/specialties", status_code=status.HTTP_201_CREATED)
def assign_specialty(
    hospital_id: int,
    request: AssignSpecialtyRequest,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Assign a specialty to a hospital (Admin only).
    
    This allows the hospital to offer appointments for this specialty.
    """
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    service = HospitalService(repository, specialty_repo)
    return service.assign_specialty_to_hospital(hospital_id, request.specialty_id)


@router.delete("/{hospital_id}/specialties/{specialty_id}", status_code=status.HTTP_200_OK)
def remove_specialty(
    hospital_id: int,
    specialty_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    Remove a specialty from a hospital (Admin only).
    
    This prevents the hospital from offering appointments for this specialty.
    """
    repository = HospitalRepository(db)
    specialty_repo = SpecialtyRepository(db)
    service = HospitalService(repository, specialty_repo)
    return service.remove_specialty_from_hospital(hospital_id, specialty_id)

