"""
Hospital Service
Business logic for hospitals
"""
from typing import List
from fastapi import HTTPException, status
from app.repositories.hospital_repository import HospitalRepository
from app.models.hospital import Hospital
from app.schemas.hospital import HospitalCreate, HospitalUpdate


class HospitalService:
    """Service for Hospital business logic"""
    
    def __init__(self, repository: HospitalRepository):
        self.repository = repository
    
    def get_all_hospitals(self, skip: int = 0, limit: int = 100) -> List[Hospital]:
        """Get all active hospitals"""
        return self.repository.get_all(skip=skip, limit=limit, active_only=True)
    
    def get_hospital_by_id(self, hospital_id: int) -> Hospital:
        """Get hospital by ID"""
        hospital = self.repository.get_by_id(hospital_id)
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital with ID {hospital_id} not found"
            )
        return hospital
    
    def create_hospital(self, hospital_data: HospitalCreate) -> Hospital:
        """Create a new hospital"""
        # Check if code already exists
        existing = self.repository.get_by_code(hospital_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hospital with code '{hospital_data.code}' already exists"
            )
        
        # Create new hospital
        new_hospital = Hospital(**hospital_data.model_dump())
        return self.repository.create(new_hospital)
    
    def update_hospital(self, hospital_id: int, hospital_data: HospitalUpdate) -> Hospital:
        """Update hospital"""
        hospital = self.get_hospital_by_id(hospital_id)
        
        # Update fields
        update_data = hospital_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hospital, field, value)
        
        return self.repository.update(hospital)
    
    def deactivate_hospital(self, hospital_id: int) -> dict:
        """Deactivate hospital"""
        hospital = self.get_hospital_by_id(hospital_id)
        
        success = self.repository.delete(hospital_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate hospital"
            )
        
        return {"message": f"Hospital '{hospital.name}' deactivated successfully"}

