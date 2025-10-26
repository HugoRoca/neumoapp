from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.consultation_room import ConsultationRoom
from app.models.specialty import Specialty


class ConsultationRoomRepository:
    """Repository for ConsultationRoom data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, room_id: int) -> Optional[ConsultationRoom]:
        """Get consultation room by ID"""
        return self.db.query(ConsultationRoom).filter(ConsultationRoom.id == room_id).first()
    
    def get_by_id_with_specialties(self, room_id: int) -> Optional[ConsultationRoom]:
        """Get consultation room by ID with specialties loaded"""
        return (
            self.db.query(ConsultationRoom)
            .options(joinedload(ConsultationRoom.specialties))
            .filter(ConsultationRoom.id == room_id)
            .first()
        )
    
    def get_by_room_number(self, room_number: str) -> Optional[ConsultationRoom]:
        """Get consultation room by room number"""
        return self.db.query(ConsultationRoom).filter(ConsultationRoom.room_number == room_number).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ConsultationRoom]:
        """Get all consultation rooms"""
        return self.db.query(ConsultationRoom).offset(skip).limit(limit).all()
    
    def get_active(self, skip: int = 0, limit: int = 100) -> List[ConsultationRoom]:
        """Get active consultation rooms"""
        return self.db.query(ConsultationRoom).filter(
            ConsultationRoom.active == True
        ).offset(skip).limit(limit).all()
    
    def get_by_hospital(self, hospital_id: int, active_only: bool = True) -> List[ConsultationRoom]:
        """Get consultation rooms for a specific hospital"""
        query = self.db.query(ConsultationRoom).filter(
            ConsultationRoom.hospital_id == hospital_id
        )
        if active_only:
            query = query.filter(ConsultationRoom.active == True)
        return query.all()
    
    def get_by_specialty(self, specialty_id: int) -> List[ConsultationRoom]:
        """Get consultation rooms assigned to a specialty"""
        return self.db.query(ConsultationRoom).join(
            ConsultationRoom.specialties
        ).filter(
            ConsultationRoom.active == True
        ).filter_by(id=specialty_id).all()
    
    def get_by_hospital_and_specialty(
        self, 
        hospital_id: int, 
        specialty_id: int, 
        active_only: bool = True
    ) -> List[ConsultationRoom]:
        """Get consultation rooms for a specific hospital and specialty"""
        query = self.db.query(ConsultationRoom).join(
            ConsultationRoom.specialties
        ).filter(
            ConsultationRoom.hospital_id == hospital_id
        ).filter(
            Specialty.id == specialty_id
        )
        if active_only:
            query = query.filter(ConsultationRoom.active == True)
        return query.all()
    
    def create(self, room: ConsultationRoom) -> ConsultationRoom:
        """Create a new consultation room"""
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room
    
    def update(self, room: ConsultationRoom) -> ConsultationRoom:
        """Update consultation room"""
        self.db.commit()
        self.db.refresh(room)
        return room
    
    def delete(self, room: ConsultationRoom) -> None:
        """Delete consultation room"""
        self.db.delete(room)
        self.db.commit()
    
    def deactivate(self, room: ConsultationRoom) -> ConsultationRoom:
        """Soft delete - deactivate consultation room"""
        room.active = False
        return self.update(room)

