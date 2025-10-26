from typing import List
from datetime import date, time, datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.appointment import Appointment, AppointmentStatus, ShiftType
from app.repositories.specialty_repository import SpecialtyRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.consultation_room_repository import ConsultationRoomRepository
from app.schemas.appointment import TimeSlot, AvailableSlotsResponse, ConsultationRoomSimple


class SlotService:
    """Service for dynamic slot generation and availability checking"""
    
    # Configuración de horarios
    MORNING_START = time(8, 0)    # 8:00 AM
    MORNING_END = time(13, 0)      # 1:00 PM
    AFTERNOON_START = time(14, 0)  # 2:00 PM
    AFTERNOON_END = time(18, 0)    # 6:00 PM
    SLOT_DURATION = 20             # minutos por consulta
    
    def __init__(self, db: Session):
        self.db = db
        self.specialty_repo = SpecialtyRepository(db)
        self.appointment_repo = AppointmentRepository(db)
        self.room_repo = ConsultationRoomRepository(db)
    
    def _is_weekday(self, check_date: date) -> bool:
        """Verifica si la fecha es día laboral (lunes a viernes)"""
        return check_date.weekday() < 5  # 0=Monday, 4=Friday
    
    def _generate_time_slots(self, start_time: time, end_time: time) -> List[time]:
        """Genera lista de horarios con intervalos de SLOT_DURATION minutos"""
        slots = []
        current_datetime = datetime.combine(date.today(), start_time)
        end_datetime = datetime.combine(date.today(), end_time)
        
        while current_datetime < end_datetime:
            slots.append(current_datetime.time())
            current_datetime += timedelta(minutes=self.SLOT_DURATION)
        
        return slots
    
    def _get_occupied_slots(
        self, 
        specialty_id: int, 
        check_date: date, 
        shift: ShiftType
    ) -> dict:
        """
        Obtiene los slots ocupados para una especialidad, fecha y turno.
        Retorna dict con estructura: {consultation_room_id: [list of occupied times]}
        """
        appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.specialty_id == specialty_id,
                Appointment.appointment_date == check_date,
                Appointment.shift == shift,
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
            )
        ).all()
        
        occupied = {}
        for apt in appointments:
            room_id = apt.consultation_room_id
            if room_id not in occupied:
                occupied[room_id] = []
            occupied[room_id].append(apt.start_time)
        
        return occupied
    
    def get_available_slots(
        self, 
        hospital_id: int,
        specialty_id: int, 
        check_date: date, 
        shift: str
    ) -> AvailableSlotsResponse:
        """
        Obtiene slots disponibles para un hospital, especialidad, fecha y turno específicos.
        
        - Genera slots dinámicamente según el turno
        - Considera múltiples consultorios del hospital
        - Filtra slots ya reservados
        - Solo días laborales (lunes a viernes)
        - Solo slots futuros si es hoy
        """
        
        # Validar que la especialidad existe
        specialty = self.specialty_repo.get_by_id(specialty_id)
        if not specialty or not specialty.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialty not found"
            )
        
        # Validar que la fecha no sea pasada
        if check_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date cannot be in the past"
            )
        
        # Validar que sea día laboral
        if not self._is_weekday(check_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointments are only available Monday through Friday"
            )
        
        # Validar turno
        try:
            shift_enum = ShiftType(shift.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid shift. Must be 'morning' or 'afternoon'"
            )
        
        # Determinar horarios según turno
        if shift_enum == ShiftType.MORNING:
            start_time = self.MORNING_START
            end_time = self.MORNING_END
        else:  # AFTERNOON
            start_time = self.AFTERNOON_START
            end_time = self.AFTERNOON_END
        
        # Generar todos los slots posibles
        time_slots = self._generate_time_slots(start_time, end_time)
        
        # Si es hoy, filtrar horarios pasados
        if check_date == date.today():
            current_time = datetime.now().time()
            time_slots = [t for t in time_slots if t > current_time]
        
        # Obtener consultorios asignados a esta especialidad en este hospital
        all_rooms = self.room_repo.get_by_specialty(specialty_id)
        consultation_rooms = [room for room in all_rooms if room.hospital_id == hospital_id and room.active]
        
        if not consultation_rooms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No consultation rooms assigned to this specialty in the selected hospital"
            )
        
        # Obtener slots ocupados
        occupied_slots = self._get_occupied_slots(specialty_id, check_date, shift_enum)
        
        # Construir respuesta con disponibilidad por consultorio
        available_slots = []
        
        for room in consultation_rooms:
            room_occupied = occupied_slots.get(room.id, [])
            
            for slot_time in time_slots:
                # Calcular end_time del slot
                slot_datetime = datetime.combine(date.today(), slot_time)
                end_datetime = slot_datetime + timedelta(minutes=self.SLOT_DURATION)
                
                is_available = slot_time not in room_occupied
                
                available_slots.append(TimeSlot(
                    start_time=slot_time,
                    end_time=end_datetime.time(),
                    consultation_room=ConsultationRoomSimple(
                        id=room.id,
                        room_number=room.room_number,
                        name=room.name
                    ),
                    available=is_available
                ))
        
        # Filtrar solo disponibles
        available_slots = [slot for slot in available_slots if slot.available]
        
        return AvailableSlotsResponse(
            specialty_id=specialty_id,
            specialty_name=specialty.name,
            date=check_date,
            shift=shift_enum.value,
            slots=available_slots
        )
    
    def validate_slot_availability(
        self, 
        specialty_id: int, 
        appointment_date: date,
        start_time: time,
        shift: str,
        consultation_room_id: int
    ) -> bool:
        """
        Valida que un slot específico esté disponible antes de crear la cita.
        
        Retorna True si está disponible, False si no.
        """
        
        # Validar que sea día laboral
        if not self._is_weekday(appointment_date):
            return False
        
        # Validar que no sea fecha pasada
        if appointment_date < date.today():
            return False
        
        # Si es hoy, validar que no sea hora pasada
        if appointment_date == date.today() and start_time <= datetime.now().time():
            return False
        
        try:
            shift_enum = ShiftType(shift.lower())
        except ValueError:
            return False
        
        # Verificar si ya existe una cita en ese slot
        existing = self.db.query(Appointment).filter(
            and_(
                Appointment.specialty_id == specialty_id,
                Appointment.appointment_date == appointment_date,
                Appointment.start_time == start_time,
                Appointment.shift == shift_enum,
                Appointment.consultation_room_id == consultation_room_id,
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
            )
        ).first()
        
        return existing is None

