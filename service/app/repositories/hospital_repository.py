"""
Hospital Repository
Handles database operations for hospitals
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.hospital import Hospital


class HospitalRepository:
    """Repository for Hospital entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Hospital]:
        """Get all hospitals"""
        query = self.db.query(Hospital)
        if active_only:
            query = query.filter(Hospital.active == True)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, hospital_id: int) -> Optional[Hospital]:
        """Get hospital by ID"""
        return self.db.query(Hospital).filter(Hospital.id == hospital_id).first()
    
    def get_by_code(self, code: str) -> Optional[Hospital]:
        """Get hospital by code"""
        return self.db.query(Hospital).filter(Hospital.code == code).first()
    
    def create(self, hospital: Hospital) -> Hospital:
        """Create a new hospital"""
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        return hospital
    
    def update(self, hospital: Hospital) -> Hospital:
        """Update hospital"""
        self.db.commit()
        self.db.refresh(hospital)
        return hospital
    
    def delete(self, hospital_id: int) -> bool:
        """Soft delete (deactivate) hospital"""
        hospital = self.get_by_id(hospital_id)
        if hospital:
            hospital.active = False
            self.db.commit()
            return True
        return False

