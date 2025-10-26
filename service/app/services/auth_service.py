from typing import Optional
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientLogin, Token
from app.repositories.patient_repository import PatientRepository
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.core.config import settings


class AuthService:
    """Service for authentication logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.patient_repo = PatientRepository(db)
    
    def register_patient(self, patient_data: PatientCreate) -> Patient:
        """Register a new patient"""
        
        # Check if document number already exists
        existing_patient = self.patient_repo.get_by_document_number(patient_data.document_number)
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document number already registered"
            )
        
        # Check if email already exists (if provided)
        if patient_data.email:
            existing_email = self.patient_repo.get_by_email(patient_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new patient
        password_hash = get_password_hash(patient_data.password)
        
        new_patient = Patient(
            document_number=patient_data.document_number,
            last_name=patient_data.last_name,
            first_name=patient_data.first_name,
            birth_date=patient_data.birth_date,
            gender=patient_data.gender,
            address=patient_data.address,
            phone=patient_data.phone,
            email=patient_data.email,
            password_hash=password_hash
        )
        
        return self.patient_repo.create(new_patient)
    
    def login(self, credentials: PatientLogin) -> Token:
        """Authenticate patient and return JWT token"""
        
        # Find patient by document number
        patient = self.patient_repo.get_by_document_number(credentials.document_number)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect document number or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(credentials.password, patient.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect document number or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if patient is active
        if not patient.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive patient"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": patient.document_number}, 
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    def get_current_patient(self, token: str) -> Patient:
        """Get current authenticated patient from token"""
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        payload = decode_token(token)
        
        if payload is None:
            raise credentials_exception
        
        document_number: str = payload.get("sub")
        if document_number is None:
            raise credentials_exception
        
        patient = self.patient_repo.get_by_document_number(document_number)
        
        if patient is None:
            raise credentials_exception
        
        if not patient.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive patient"
            )
        
        return patient
