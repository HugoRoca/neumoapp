from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.patient import Patient


class PatientRepository:
    """Repository for Patient data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        return self.db.query(Patient).filter(Patient.id == patient_id).first()
    
    def get_by_document_number(self, document_number: str) -> Optional[Patient]:
        """Get patient by document number"""
        return self.db.query(Patient).filter(Patient.document_number == document_number).first()
    
    def get_by_email(self, email: str) -> Optional[Patient]:
        """Get patient by email"""
        return self.db.query(Patient).filter(Patient.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Get all patients with pagination"""
        return self.db.query(Patient).offset(skip).limit(limit).all()
    
    def get_active(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Get active patients"""
        return self.db.query(Patient).filter(Patient.active == True).offset(skip).limit(limit).all()
    
    def create(self, patient: Patient) -> Patient:
        """Create a new patient"""
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def update(self, patient: Patient) -> Patient:
        """Update patient"""
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def delete(self, patient: Patient) -> None:
        """Delete patient"""
        self.db.delete(patient)
        self.db.commit()
    
    def deactivate(self, patient: Patient) -> Patient:
        """Soft delete - deactivate patient"""
        patient.active = False
        return self.update(patient)
