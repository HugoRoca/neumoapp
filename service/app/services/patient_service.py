from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository


class PatientService:
    """Service for patient business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.patient_repo = PatientRepository(db)
    
    def get_patient_by_id(self, patient_id: int) -> Patient:
        """Get patient by ID"""
        patient = self.patient_repo.get_by_id(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return patient
    
    def get_all_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Get all patients"""
        return self.patient_repo.get_all(skip, limit)
    
    def get_active_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Get active patients"""
        return self.patient_repo.get_active(skip, limit)
    
    def update_patient(self, patient: Patient) -> Patient:
        """Update patient information"""
        return self.patient_repo.update(patient)
    
    def deactivate_patient(self, patient_id: int) -> Patient:
        """Deactivate patient"""
        patient = self.get_patient_by_id(patient_id)
        return self.patient_repo.deactivate(patient)
