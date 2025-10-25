from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String(20), unique=True, index=True, nullable=False)
    lastname = Column(String(100), nullable=False)
    firstname = Column(String(100), nullable=False)
    date_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)  # Male, Female, Other
    address = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    civil_status = Column(String(50), nullable=True)  # Single, Married, Divorced, Widowed
    password_hash = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con citas
    appointments = relationship("Appointment", back_populates="patient")

