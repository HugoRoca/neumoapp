from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.specialty import Specialty


class SpecialtyRepository:
    """Repository for Specialty data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, specialty_id: int) -> Optional[Specialty]:
        """Get specialty by ID"""
        return self.db.query(Specialty).filter(Specialty.id == specialty_id).first()
    
    def get_by_name(self, name: str) -> Optional[Specialty]:
        """Get specialty by name"""
        return self.db.query(Specialty).filter(Specialty.name == name).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Specialty]:
        """Get all specialties"""
        return self.db.query(Specialty).offset(skip).limit(limit).all()
    
    def get_active(self, skip: int = 0, limit: int = 100) -> List[Specialty]:
        """Get active specialties"""
        return self.db.query(Specialty).filter(
            Specialty.active == True
        ).offset(skip).limit(limit).all()
    
    def create(self, specialty: Specialty) -> Specialty:
        """Create a new specialty"""
        self.db.add(specialty)
        self.db.commit()
        self.db.refresh(specialty)
        return specialty
    
    def update(self, specialty: Specialty) -> Specialty:
        """Update specialty"""
        self.db.commit()
        self.db.refresh(specialty)
        return specialty
    
    def delete(self, specialty: Specialty) -> None:
        """Delete specialty"""
        self.db.delete(specialty)
        self.db.commit()
