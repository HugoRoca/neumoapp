"""
Hospital Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


# Tabla de asociación: hospitales <-> especialidades (muchos a muchos)
hospital_specialties = Table(
    'hospital_specialties',
    Base.metadata,
    Column('hospital_id', Integer, ForeignKey('hospitals.id', ondelete='CASCADE'), primary_key=True),
    Column('specialty_id', Integer, ForeignKey('specialties.id', ondelete='CASCADE'), primary_key=True),
    Column('active', Boolean, default=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)


class Hospital(Base):
    """Hospital entity"""
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=False)
    district = Column(String(100))
    city = Column(String(100), default="Lima")
    phone = Column(String(20))
    email = Column(String(100))
    description = Column(Text)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    consultation_rooms = relationship("ConsultationRoom", back_populates="hospital")
    
    # Relación muchos a muchos con especialidades
    specialties = relationship(
        "Specialty",
        secondary=hospital_specialties,
        back_populates="hospitals"
    )
    
    def __repr__(self):
        return f"<Hospital(id={self.id}, name='{self.name}', code='{self.code}')>"

