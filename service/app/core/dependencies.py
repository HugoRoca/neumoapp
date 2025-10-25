from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.core.security import decode_token
from app.models.patient import Patient

security = HTTPBearer()


async def get_current_patient(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Patient:
    """Get current patient from JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    document_number: str = payload.get("sub")
    if document_number is None:
        raise credentials_exception
    
    patient = db.query(Patient).filter(Patient.document_number == document_number).first()
    
    if patient is None:
        raise credentials_exception
    
    if not patient.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive patient"
        )
    
    return patient
