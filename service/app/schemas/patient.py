from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date


class PatientBase(BaseModel):
    document_number: str = Field(..., min_length=8, max_length=20, description="Document number (DNI/ID)")
    last_name: str = Field(..., min_length=2, max_length=100, description="Last name")
    first_name: str = Field(..., min_length=2, max_length=100, description="First name")
    birth_date: date = Field(..., description="Date of birth")
    gender: str = Field(..., pattern="^[MF]$", description="Gender: M (Male) or F (Female)")
    address: Optional[str] = Field(None, max_length=255, description="Address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: EmailStr


class PatientCreate(PatientBase):
    password: str = Field(..., min_length=6, max_length=50)


class PatientLogin(BaseModel):
    document_number: str = Field(..., description="Document number (DNI/ID)")
    password: str = Field(..., description="Password")


class PatientResponse(PatientBase):
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    document_number: Optional[str] = None

