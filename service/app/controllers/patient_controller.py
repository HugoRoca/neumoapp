from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.schemas.patient import PatientResponse
from app.services.patient_service import PatientService
from app.core.dependencies import get_current_patient
from app.models.patient import Patient

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """List all active patients (admin only)"""
    service = PatientService(db)
    return service.get_active_patients(skip, limit)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient)
):
    """Get patient by ID (admin only)"""
    service = PatientService(db)
    return service.get_patient_by_id(patient_id)
