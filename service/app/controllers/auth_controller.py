from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.patient import PatientCreate, PatientLogin, PatientResponse, Token
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_patient
from app.models.patient import Patient

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Register a new patient in the system
    
    - **document_number**: Unique identification document
    - **lastname**: Patient's last name
    - **firstname**: Patient's first name
    - **password**: Password (min 6 characters)
    """
    service = AuthService(db)
    return service.register_patient(patient)


@router.post("/login", response_model=Token)
async def login(credentials: PatientLogin, db: Session = Depends(get_db)):
    """
    Login with document number and password
    
    Returns JWT access token
    """
    service = AuthService(db)
    return service.login(credentials)


@router.get("/me", response_model=PatientResponse)
async def get_my_profile(
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get authenticated patient profile"""
    return current_patient
