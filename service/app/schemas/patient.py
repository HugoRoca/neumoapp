from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date


class PatientBase(BaseModel):
    document_number: str = Field(..., min_length=8, max_length=20, description="Document number (DNI/ID)")
    lastname: str = Field(..., min_length=2, max_length=100, description="Last name")
    firstname: str = Field(..., min_length=2, max_length=100, description="First name")
    date_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, max_length=20, description="Gender: Male, Female, Other")
    address: Optional[str] = Field(None, max_length=255, description="Address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: Optional[EmailStr] = None
    civil_status: Optional[str] = Field(None, max_length=50, description="Civil status: Single, Married, Divorced, Widowed")


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

