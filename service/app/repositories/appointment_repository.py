from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.appointment import Appointment, AppointmentStatus


class AppointmentRepository:
    """Repository for Appointment data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID"""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    def get_by_patient(
        self, 
        patient_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Appointment]:
        """Get appointments by patient, ordered by date and time"""
        return self.db.query(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(
            Appointment.appointment_date.desc(),
            Appointment.start_time.desc()
        ).offset(skip).limit(limit).all()
    
    def get_upcoming_by_patient(
        self, 
        patient_id: int,
        from_date: date,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Appointment]:
        """Get upcoming appointments for a patient"""
        return self.db.query(Appointment).filter(
            and_(
                Appointment.patient_id == patient_id,
                Appointment.appointment_date >= from_date,
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
            )
        ).order_by(
            Appointment.appointment_date.asc(),
            Appointment.start_time.asc()
        ).offset(skip).limit(limit).all()
    
    def get_by_status(
        self, 
        status: AppointmentStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Appointment]:
        """Get appointments by status"""
        return self.db.query(Appointment).filter(
            Appointment.status == status
        ).offset(skip).limit(limit).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """Get all appointments"""
        return self.db.query(Appointment).offset(skip).limit(limit).all()
    
    def create(self, appointment: Appointment) -> Appointment:
        """Create a new appointment"""
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
    
    def update(self, appointment: Appointment) -> Appointment:
        """Update appointment"""
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
    
    def delete(self, appointment: Appointment) -> None:
        """Delete appointment"""
        self.db.delete(appointment)
        self.db.commit()
    
    def cancel(self, appointment: Appointment) -> Appointment:
        """Cancel appointment"""
        appointment.status = AppointmentStatus.CANCELLED
        return self.update(appointment)
