from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.base import Base


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ShiftType(str, enum.Enum):
    MORNING = "morning"  # 8:00 - 13:00
    AFTERNOON = "afternoon"  # 14:00 - 18:00


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)
    consultation_room_id = Column(Integer, ForeignKey("consultation_rooms.id"), nullable=False)  # FK a consultation_rooms
    
    # Nueva estructura: fecha, hora y turno
    appointment_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    shift = Column(Enum(ShiftType), nullable=False)
    
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING, index=True)
    reason = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    patient = relationship("Patient", back_populates="appointments")
    specialty = relationship("Specialty", back_populates="appointments")
    consultation_room = relationship("ConsultationRoom", back_populates="appointments")

