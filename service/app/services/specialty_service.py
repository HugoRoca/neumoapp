from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.specialty import Specialty
from app.schemas.specialty import SpecialtyCreate
from app.repositories.specialty_repository import SpecialtyRepository


class SpecialtyService:
    """Service for specialty business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.specialty_repo = SpecialtyRepository(db)
    
    def get_all_specialties(self, skip: int = 0, limit: int = 100) -> List[Specialty]:
        """Get all active specialties"""
        return self.specialty_repo.get_active(skip, limit)
    
    def get_specialty_by_id(self, specialty_id: int) -> Specialty:
        """Get specialty by ID"""
        specialty = self.specialty_repo.get_by_id(specialty_id)
        
        if not specialty or not specialty.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialty not found"
            )
        
        return specialty
    
    def create_specialty(self, specialty_data: SpecialtyCreate) -> Specialty:
        """Create a new specialty"""
        
        # Check if already exists
        existing = self.specialty_repo.get_by_name(specialty_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialty already exists"
            )
        
        new_specialty = Specialty(**specialty_data.model_dump())
        return self.specialty_repo.create(new_specialty)
