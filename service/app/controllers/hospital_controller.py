"""
Hospital Controller
Handles HTTP requests for hospitals
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.schemas.hospital import HospitalResponse, HospitalCreate, HospitalUpdate
from app.repositories.hospital_repository import HospitalRepository
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
    """Get all hospitals"""
    repository = HospitalRepository(db)
    service = HospitalService(repository)
    return service.get_all_hospitals(skip=skip, limit=limit)


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Get hospital by ID"""
    repository = HospitalRepository(db)
    service = HospitalService(repository)
    return service.get_hospital_by_id(hospital_id)


@router.post("/", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
def create_hospital(
    hospital: HospitalCreate,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Create a new hospital (Admin only)"""
    repository = HospitalRepository(db)
    service = HospitalService(repository)
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
    service = HospitalService(repository)
    return service.update_hospital(hospital_id, hospital)


@router.delete("/{hospital_id}", status_code=status.HTTP_200_OK)
def deactivate_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Deactivate hospital (Admin only)"""
    repository = HospitalRepository(db)
    service = HospitalService(repository)
    return service.deactivate_hospital(hospital_id)

