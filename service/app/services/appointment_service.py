from typing import List
from datetime import date, datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus, ShiftType
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.specialty_repository import SpecialtyRepository
from app.repositories.consultation_room_repository import ConsultationRoomRepository
from app.repositories.hospital_repository import HospitalRepository
from app.services.slot_service import SlotService


class AppointmentService:
    """Service for appointment business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.appointment_repo = AppointmentRepository(db)
        self.specialty_repo = SpecialtyRepository(db)
        self.room_repo = ConsultationRoomRepository(db)
        self.hospital_repo = HospitalRepository(db)
        self.slot_service = SlotService(db)
    
    def book_appointment(
        self, 
        appointment_data: AppointmentCreate, 
        current_patient: Patient
    ) -> Appointment:
        """Book a new appointment"""
        
        # Check if specialty exists
        specialty = self.specialty_repo.get_by_id(appointment_data.specialty_id)
        if not specialty or not specialty.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialty not found"
            )
        
        # Validate consultation room exists and is assigned to specialty
        consultation_room = self.room_repo.get_by_id_with_specialties(appointment_data.consultation_room_id)
        if not consultation_room or not consultation_room.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation room not found"
            )
        
        # Verify room is assigned to this specialty
        if specialty not in consultation_room.specialties:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This consultation room is not assigned to the selected specialty"
            )
        
        # Verify hospital offers this specialty
        hospital = consultation_room.hospital
        if not self.hospital_repo.has_specialty(hospital.id, specialty.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hospital '{hospital.name}' does not offer the specialty '{specialty.name}'"
            )
        
        # Validate slot availability
        is_available = self.slot_service.validate_slot_availability(
            specialty_id=appointment_data.specialty_id,
            appointment_date=appointment_data.appointment_date,
            start_time=appointment_data.start_time,
            shift=appointment_data.shift,
            consultation_room_id=appointment_data.consultation_room_id
        )
        
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This time slot is not available"
            )
        
        # Calculate end time (20 minutes after start)
        start_datetime = datetime.combine(date.today(), appointment_data.start_time)
        end_datetime = start_datetime + timedelta(minutes=20)
        end_time = end_datetime.time()
        
        # Validate shift
        try:
            shift_enum = ShiftType(appointment_data.shift.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid shift. Must be 'morning' or 'afternoon'"
            )
        
        # Create appointment
        new_appointment = Appointment(
            patient_id=current_patient.id,
            specialty_id=appointment_data.specialty_id,
            consultation_room_id=appointment_data.consultation_room_id,
            appointment_date=appointment_data.appointment_date,
            start_time=appointment_data.start_time,
            end_time=end_time,
            shift=shift_enum,
            reason=appointment_data.reason,
            status=AppointmentStatus.PENDING
        )
        
        return self.appointment_repo.create(new_appointment)
    
    def get_my_appointments(
        self, 
        current_patient: Patient, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Appointment]:
        """Get all appointments for current patient"""
        return self.appointment_repo.get_by_patient(current_patient.id, skip, limit)
    
    def get_upcoming_appointments(
        self, 
        current_patient: Patient, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Appointment]:
        """Get upcoming appointments for current patient"""
        return self.appointment_repo.get_upcoming_by_patient(
            current_patient.id, 
            date.today(),
            skip, 
            limit
        )
    
    def get_appointment_by_id(
        self, 
        appointment_id: int, 
        current_patient: Patient
    ) -> Appointment:
        """Get appointment by ID"""
        appointment = self.appointment_repo.get_by_id(appointment_id)
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Verify appointment belongs to current patient
        if appointment.patient_id != current_patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this appointment"
            )
        
        return appointment
    
    def update_appointment(
        self, 
        appointment_id: int, 
        appointment_update: AppointmentUpdate, 
        current_patient: Patient
    ) -> Appointment:
        """Update appointment status or observations"""
        
        appointment = self.get_appointment_by_id(appointment_id, current_patient)
        
        # Update fields if provided
        if appointment_update.status:
            try:
                status_enum = AppointmentStatus(appointment_update.status)
                appointment.status = status_enum
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status. Must be: pending, confirmed, cancelled, completed"
                )
        
        if appointment_update.observations is not None:
            appointment.observations = appointment_update.observations
        
        return self.appointment_repo.update(appointment)
    
    def cancel_appointment(
        self, 
        appointment_id: int, 
        current_patient: Patient
    ) -> dict:
        """Cancel an appointment (slot becomes available again automatically)"""
        
        appointment = self.get_appointment_by_id(appointment_id, current_patient)
        
        # Only pending or confirmed appointments can be cancelled
        if appointment.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending or confirmed appointments can be cancelled"
            )
        
        # Change status to cancelled (slot automatically becomes available)
        self.appointment_repo.cancel(appointment)
        
        return {"message": "Appointment cancelled successfully"}
