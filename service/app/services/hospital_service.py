"""
Hospital Service
Business logic for hospitals
"""
from typing import List
from fastapi import HTTPException, status
from app.repositories.hospital_repository import HospitalRepository
from app.repositories.specialty_repository import SpecialtyRepository
from app.models.hospital import Hospital
from app.models.specialty import Specialty
from app.schemas.hospital import HospitalCreate, HospitalUpdate


class HospitalService:
    """Service for Hospital business logic"""
    
    def __init__(self, repository: HospitalRepository, specialty_repository: SpecialtyRepository):
        self.repository = repository
        self.specialty_repository = specialty_repository
    
    def get_all_hospitals(self, skip: int = 0, limit: int = 100) -> List[Hospital]:
        """Get all active hospitals"""
        return self.repository.get_all(skip=skip, limit=limit, active_only=True)
    
    def get_hospital_by_id(self, hospital_id: int) -> Hospital:
        """Get hospital by ID"""
        hospital = self.repository.get_by_id(hospital_id)
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital with ID {hospital_id} not found"
            )
        return hospital
    
    def get_hospital_with_specialties(self, hospital_id: int) -> Hospital:
        """Get hospital by ID with specialties loaded"""
        hospital = self.repository.get_by_id_with_specialties(hospital_id)
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hospital with ID {hospital_id} not found"
            )
        return hospital
    
    def create_hospital(self, hospital_data: HospitalCreate) -> Hospital:
        """Create a new hospital"""
        # Check if code already exists
        existing = self.repository.get_by_code(hospital_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hospital with code '{hospital_data.code}' already exists"
            )
        
        # Extract specialty_ids
        specialty_ids = hospital_data.specialty_ids if hasattr(hospital_data, 'specialty_ids') else []
        hospital_dict = hospital_data.model_dump(exclude={'specialty_ids'})
        
        # Create new hospital
        new_hospital = Hospital(**hospital_dict)
        created_hospital = self.repository.create(new_hospital)
        
        # Assign specialties if provided
        if specialty_ids:
            for specialty_id in specialty_ids:
                specialty = self.specialty_repository.get_by_id(specialty_id)
                if specialty:
                    self.repository.add_specialty(created_hospital.id, specialty)
        
        return self.get_hospital_with_specialties(created_hospital.id)
    
    def update_hospital(self, hospital_id: int, hospital_data: HospitalUpdate) -> Hospital:
        """Update hospital"""
        hospital = self.get_hospital_by_id(hospital_id)
        
        # Update fields
        update_data = hospital_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hospital, field, value)
        
        return self.repository.update(hospital)
    
    def deactivate_hospital(self, hospital_id: int) -> dict:
        """Deactivate hospital"""
        hospital = self.get_hospital_by_id(hospital_id)
        
        success = self.repository.delete(hospital_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate hospital"
            )
        
        return {"message": f"Hospital '{hospital.name}' deactivated successfully"}
    
    # Métodos para gestionar especialidades
    
    def get_hospital_specialties(self, hospital_id: int) -> List[Specialty]:
        """Get all specialties for a hospital"""
        # Verificar que el hospital existe
        self.get_hospital_by_id(hospital_id)
        
        return self.repository.get_specialties(hospital_id, active_only=True)
    
    def assign_specialty_to_hospital(self, hospital_id: int, specialty_id: int) -> dict:
        """Assign a specialty to a hospital"""
        # Verificar que el hospital existe
        self.get_hospital_by_id(hospital_id)
        
        # Verificar que la especialidad existe
        specialty = self.specialty_repository.get_by_id(specialty_id)
        if not specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Specialty with ID {specialty_id} not found"
            )
        
        # Verificar si ya está asignada
        if self.repository.has_specialty(hospital_id, specialty_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Specialty '{specialty.name}' is already assigned to this hospital"
            )
        
        # Asignar especialidad
        success = self.repository.add_specialty(hospital_id, specialty)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to assign specialty"
            )
        
        return {
            "message": f"Specialty '{specialty.name}' assigned successfully",
            "specialty_id": specialty_id,
            "hospital_id": hospital_id
        }
    
    def remove_specialty_from_hospital(self, hospital_id: int, specialty_id: int) -> dict:
        """Remove a specialty from a hospital"""
        # Verificar que el hospital existe
        self.get_hospital_by_id(hospital_id)
        
        # Verificar que la especialidad existe
        specialty = self.specialty_repository.get_by_id(specialty_id)
        if not specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Specialty with ID {specialty_id} not found"
            )
        
        # Verificar si está asignada
        if not self.repository.has_specialty(hospital_id, specialty_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Specialty '{specialty.name}' is not assigned to this hospital"
            )
        
        # Remover especialidad
        success = self.repository.remove_specialty(hospital_id, specialty)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove specialty"
            )
        
        return {
            "message": f"Specialty '{specialty.name}' removed successfully",
            "specialty_id": specialty_id,
            "hospital_id": hospital_id
        }

