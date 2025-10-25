from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


# Tabla de asociación: especialidades <-> consultorios (muchos a muchos)
specialty_rooms = Table(
    'specialty_consultation_rooms',
    Base.metadata,
    Column('specialty_id', Integer, ForeignKey('specialties.id', ondelete='CASCADE'), primary_key=True),
    Column('consultation_room_id', Integer, ForeignKey('consultation_rooms.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class ConsultationRoom(Base):
    __tablename__ = "consultation_rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), unique=True, nullable=False)  # Ej: "101", "A-1", "CARD-1"
    name = Column(String(100), nullable=False)  # Ej: "Consultorio Cardiología 1"
    floor = Column(String(20), nullable=True)  # Ej: "1", "2", "PB"
    building = Column(String(50), nullable=True)  # Ej: "Edificio A", "Torre Principal"
    description = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación muchos a muchos con especialidades
    specialties = relationship(
        "Specialty",
        secondary=specialty_rooms,
        back_populates="consultation_rooms"
    )
    
    # Relación con appointments
    appointments = relationship("Appointment", back_populates="consultation_room")

