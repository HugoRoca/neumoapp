from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.consultation_room import ConsultationRoom
from app.models.specialty import Specialty
from app.schemas.consultation_room import ConsultationRoomCreate, ConsultationRoomUpdate
from app.repositories.consultation_room_repository import ConsultationRoomRepository
from app.repositories.specialty_repository import SpecialtyRepository


class ConsultationRoomService:
    """Service for consultation room business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.room_repo = ConsultationRoomRepository(db)
        self.specialty_repo = SpecialtyRepository(db)
    
    def get_all_rooms(self, skip: int = 0, limit: int = 100) -> List[ConsultationRoom]:
        """Get all active consultation rooms"""
        return self.room_repo.get_active(skip, limit)
    
    def get_room_by_id(self, room_id: int) -> ConsultationRoom:
        """Get consultation room by ID"""
        room = self.room_repo.get_by_id(room_id)
        
        if not room or not room.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation room not found"
            )
        
        return room
    
    def get_rooms_by_specialty(self, specialty_id: int) -> List[ConsultationRoom]:
        """Get consultation rooms assigned to a specialty"""
        # Verify specialty exists
        specialty = self.specialty_repo.get_by_id(specialty_id)
        if not specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialty not found"
            )
        
        return self.room_repo.get_by_specialty(specialty_id)
    
    def create_room(self, room_data: ConsultationRoomCreate) -> ConsultationRoom:
        """Create a new consultation room"""
        
        # Check if room number already exists
        existing = self.room_repo.get_by_room_number(room_data.room_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room number already exists"
            )
        
        # Create room
        new_room = ConsultationRoom(
            room_number=room_data.room_number,
            name=room_data.name,
            floor=room_data.floor,
            building=room_data.building,
            description=room_data.description
        )
        
        # Assign specialties if provided
        if room_data.specialty_ids:
            for specialty_id in room_data.specialty_ids:
                specialty = self.specialty_repo.get_by_id(specialty_id)
                if specialty and specialty.active:
                    new_room.specialties.append(specialty)
        
        return self.room_repo.create(new_room)
    
    def update_room(self, room_id: int, room_update: ConsultationRoomUpdate) -> ConsultationRoom:
        """Update consultation room"""
        
        room = self.get_room_by_id(room_id)
        
        # Update fields if provided
        if room_update.name is not None:
            room.name = room_update.name
        if room_update.floor is not None:
            room.floor = room_update.floor
        if room_update.building is not None:
            room.building = room_update.building
        if room_update.description is not None:
            room.description = room_update.description
        if room_update.active is not None:
            room.active = room_update.active
        
        # Update specialty assignments if provided
        if room_update.specialty_ids is not None:
            room.specialties.clear()
            for specialty_id in room_update.specialty_ids:
                specialty = self.specialty_repo.get_by_id(specialty_id)
                if specialty and specialty.active:
                    room.specialties.append(specialty)
        
        return self.room_repo.update(room)
    
    def assign_specialty(self, room_id: int, specialty_id: int) -> ConsultationRoom:
        """Assign a specialty to a consultation room"""
        
        room = self.get_room_by_id(room_id)
        specialty = self.specialty_repo.get_by_id(specialty_id)
        
        if not specialty or not specialty.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialty not found"
            )
        
        # Check if already assigned
        if specialty in room.specialties:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialty already assigned to this room"
            )
        
        room.specialties.append(specialty)
        return self.room_repo.update(room)
    
    def remove_specialty(self, room_id: int, specialty_id: int) -> ConsultationRoom:
        """Remove a specialty from a consultation room"""
        
        room = self.get_room_by_id(room_id)
        specialty = self.specialty_repo.get_by_id(specialty_id)
        
        if not specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialty not found"
            )
        
        # Check if assigned
        if specialty not in room.specialties:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specialty not assigned to this room"
            )
        
        room.specialties.remove(specialty)
        return self.room_repo.update(room)
    
    def deactivate_room(self, room_id: int) -> ConsultationRoom:
        """Deactivate consultation room"""
        room = self.get_room_by_id(room_id)
        return self.room_repo.deactivate(room)

