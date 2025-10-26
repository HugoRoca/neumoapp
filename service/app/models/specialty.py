from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    appointments = relationship("Appointment", back_populates="specialty")
    
    # Relación muchos a muchos con hospitales
    hospitals = relationship(
        "Hospital",
        secondary="hospital_specialties",
        back_populates="specialties"
    )
    
    # Relación muchos a muchos con consultorios
    consultation_rooms = relationship(
        "ConsultationRoom",
        secondary="specialty_consultation_rooms",
        back_populates="specialties"
    )

