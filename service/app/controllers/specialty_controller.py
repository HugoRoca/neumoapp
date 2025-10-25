from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.schemas.specialty import SpecialtyResponse, SpecialtyCreate
from app.services.specialty_service import SpecialtyService
from app.core.dependencies import get_current_patient
from app.models.patient import Patient

router = APIRouter(prefix="/specialties", tags=["Specialties"])


@router.get("/", response_model=List[SpecialtyResponse])
async def list_specialties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """
    List all active medical specialties
    
    Available specialties for appointment booking
    """
    service = SpecialtyService(db)
    return service.get_all_specialties(skip, limit)


@router.get("/{specialty_id}", response_model=SpecialtyResponse)
async def get_specialty(
    specialty_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Get specialty details by ID"""
    service = SpecialtyService(db)
    return service.get_specialty_by_id(specialty_id)


@router.post("/", response_model=SpecialtyResponse, status_code=status.HTTP_201_CREATED)
async def create_specialty(
    specialty: SpecialtyCreate,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Create a new specialty (admin only)"""
    service = SpecialtyService(db)
    return service.create_specialty(specialty)
