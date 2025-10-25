"""
Script to initialize the database with sample data
NEW VERSION with Dynamic Scheduling System + Consultation Rooms
"""
from datetime import date, time, timedelta
from app.database.base import SessionLocal, engine, Base
from app.models.patient import Patient
from app.models.specialty import Specialty
from app.models.consultation_room import ConsultationRoom
from app.models.appointment import Appointment, AppointmentStatus, ShiftType
from app.core.security import get_password_hash


def init_db():
    """Initialize database with sample data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Patient).first() or db.query(Specialty).first():
            print("⚠️  Database already contains data. Will not reinitialize.")
            print("   To start fresh, drop the database and run again.")
            return
        
        print("\n" + "="*60)
        print("🚀 INITIALIZING DATABASE - System with Consultation Rooms")
        print("="*60 + "\n")
        
        # =====================================================
        # Create sample patients
        # =====================================================
        print("📝 Creating patients...")
        
        patients = [
            Patient(
                document_number="12345678",
                lastname="Pérez",
                firstname="Juan",
                date_birth=date(1985, 5, 15),
                gender="Male",
                address="Av. Example 123, Lima",
                phone="987654321",
                email="juan.perez@example.com",
                civil_status="Married",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="87654321",
                lastname="González",
                firstname="María",
                date_birth=date(1990, 8, 22),
                gender="Female",
                address="Jr. Sample 456, Lima",
                phone="912345678",
                email="maria.gonzalez@example.com",
                civil_status="Single",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="11111111",
                lastname="Rodríguez",
                firstname="Pedro",
                date_birth=date(1978, 3, 10),
                gender="Male",
                address="Calle Test 789, Lima",
                phone="999888777",
                email="pedro.rodriguez@example.com",
                civil_status="Divorced",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="22222222",
                lastname="Martínez",
                firstname="Ana",
                date_birth=date(1995, 12, 5),
                gender="Female",
                address="Av. Demo 321, Lima",
                phone="988777666",
                email="ana.martinez@example.com",
                civil_status="Single",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="33333333",
                lastname="López",
                firstname="Carlos",
                date_birth=date(1982, 7, 18),
                gender="Male",
                address="Jr. Testing 555, Lima",
                phone="977666555",
                email="carlos.lopez@example.com",
                civil_status="Married",
                password_hash=get_password_hash("password123")
            ),
        ]
        
        db.add_all(patients)
        db.commit()
        print(f"   ✓ Created {len(patients)} patients")
        
        # =====================================================
        # Create specialties
        # =====================================================
        print("\n🏥 Creating medical specialties...")
        
        specialties = [
            Specialty(
                name="Medicina General",
                description="Consulta general y diagnóstico inicial"
            ),
            Specialty(
                name="Cardiología",
                description="Especialista en enfermedades del corazón"
            ),
            Specialty(
                name="Pediatría",
                description="Atención médica para niños y adolescentes"
            ),
            Specialty(
                name="Dermatología",
                description="Especialista en enfermedades de la piel"
            ),
            Specialty(
                name="Ginecología",
                description="Salud reproductiva femenina"
            ),
            Specialty(
                name="Traumatología",
                description="Especialista en lesiones del sistema músculo-esquelético"
            ),
            Specialty(
                name="Oftalmología",
                description="Especialista en enfermedades de los ojos"
            ),
            Specialty(
                name="Neurología",
                description="Especialista en el sistema nervioso"
            ),
            Specialty(
                name="Psicología",
                description="Salud mental y bienestar emocional"
            ),
            Specialty(
                name="Nutrición",
                description="Asesoramiento nutricional y dietético"
            ),
        ]
        
        db.add_all(specialties)
        db.commit()
        print(f"   ✓ Created {len(specialties)} specialties")
        
        # =====================================================
        # Create consultation rooms
        # =====================================================
        print("\n🏢 Creating consultation rooms...")
        
        consultation_rooms = [
            # Medicina General (3 consultorios)
            ConsultationRoom(
                room_number="GRAL-101",
                name="Consultorio Medicina General 1",
                floor="1",
                building="Edificio A",
                description="Equipado para consultas generales"
            ),
            ConsultationRoom(
                room_number="GRAL-102",
                name="Consultorio Medicina General 2",
                floor="1",
                building="Edificio A",
                description="Equipado para consultas generales"
            ),
            ConsultationRoom(
                room_number="GRAL-103",
                name="Consultorio Medicina General 3",
                floor="1",
                building="Edificio A",
                description="Equipado para consultas generales"
            ),
            # Cardiología (2 consultorios)
            ConsultationRoom(
                room_number="CARD-201",
                name="Consultorio Cardiología 1",
                floor="2",
                building="Edificio A",
                description="Equipado con ECG"
            ),
            ConsultationRoom(
                room_number="CARD-202",
                name="Consultorio Cardiología 2",
                floor="2",
                building="Edificio A",
                description="Equipado con ECG y monitor Holter"
            ),
            # Pediatría (2 consultorios)
            ConsultationRoom(
                room_number="PED-301",
                name="Consultorio Pediatría 1",
                floor="3",
                building="Edificio B",
                description="Ambiente infantil"
            ),
            ConsultationRoom(
                room_number="PED-302",
                name="Consultorio Pediatría 2",
                floor="3",
                building="Edificio B",
                description="Ambiente infantil"
            ),
            # Dermatología (1 consultorio)
            ConsultationRoom(
                room_number="DERM-401",
                name="Consultorio Dermatología",
                floor="4",
                building="Edificio B",
                description="Equipado con dermatoscopio"
            ),
            # Ginecología (1 consultorio)
            ConsultationRoom(
                room_number="GINE-402",
                name="Consultorio Ginecología",
                floor="4",
                building="Edificio B",
                description="Equipado para consultas ginecológicas"
            ),
            # Traumatología (2 consultorios)
            ConsultationRoom(
                room_number="TRAU-501",
                name="Consultorio Traumatología 1",
                floor="5",
                building="Edificio A",
                description="Equipado para evaluación musculoesquelética"
            ),
            ConsultationRoom(
                room_number="TRAU-502",
                name="Consultorio Traumatología 2",
                floor="5",
                building="Edificio A",
                description="Equipado para evaluación musculoesquelética"
            ),
            # Oftalmología (1 consultorio)
            ConsultationRoom(
                room_number="OFTA-601",
                name="Consultorio Oftalmología",
                floor="6",
                building="Edificio A",
                description="Equipado con oftalmoscopio y tonómetro"
            ),
            # Neurología (1 consultorio)
            ConsultationRoom(
                room_number="NEUR-602",
                name="Consultorio Neurología",
                floor="6",
                building="Edificio A",
                description="Equipado para examen neurológico"
            ),
            # Psicología (2 consultorios)
            ConsultationRoom(
                room_number="PSI-701",
                name="Consultorio Psicología 1",
                floor="7",
                building="Edificio B",
                description="Ambiente privado y confortable"
            ),
            ConsultationRoom(
                room_number="PSI-702",
                name="Consultorio Psicología 2",
                floor="7",
                building="Edificio B",
                description="Ambiente privado y confortable"
            ),
            # Nutrición (1 consultorio)
            ConsultationRoom(
                room_number="NUTR-703",
                name="Consultorio Nutrición",
                floor="7",
                building="Edificio B",
                description="Equipado con balanza y medidor de composición corporal"
            ),
        ]
        
        db.add_all(consultation_rooms)
        db.commit()
        print(f"   ✓ Created {len(consultation_rooms)} consultation rooms")
        
        # =====================================================
        # Assign consultation rooms to specialties
        # =====================================================
        print("\n🔗 Assigning consultation rooms to specialties...")
        
        # Refresh to get IDs
        for s in specialties:
            db.refresh(s)
        for cr in consultation_rooms:
            db.refresh(cr)
        
        # Assignment map: (specialty_name, [room_numbers])
        assignments = {
            "Medicina General": ["GRAL-101", "GRAL-102", "GRAL-103"],
            "Cardiología": ["CARD-201", "CARD-202"],
            "Pediatría": ["PED-301", "PED-302"],
            "Dermatología": ["DERM-401"],
            "Ginecología": ["GINE-402"],
            "Traumatología": ["TRAU-501", "TRAU-502"],
            "Oftalmología": ["OFTA-601"],
            "Neurología": ["NEUR-602"],
            "Psicología": ["PSI-701", "PSI-702"],
            "Nutrición": ["NUTR-703"],
        }
        
        assignment_count = 0
        for specialty_name, room_numbers in assignments.items():
            specialty = next(s for s in specialties if s.name == specialty_name)
            for room_number in room_numbers:
                room = next(cr for cr in consultation_rooms if cr.room_number == room_number)
                specialty.consultation_rooms.append(room)
                assignment_count += 1
        
        db.commit()
        print(f"   ✓ Created {assignment_count} specialty-room assignments")
        print(f"   ✓ Total rooms available: {len(consultation_rooms)}")
        
        # =====================================================
        # Create sample appointments
        # =====================================================
        print("\n📅 Creating sample appointments...")
        
        # Already refreshed above
        
        # Get today's date and next working days
        today = date.today()
        
        # Find next Monday if today is weekend
        days_ahead = 0 - today.weekday()  # Monday is 0
        if days_ahead <= 0:  # Target day already happened this week or today
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)
        
        # Get consultation rooms by specialty
        card_room = next(cr for cr in consultation_rooms if cr.room_number == "CARD-201")
        derm_room = next(cr for cr in consultation_rooms if cr.room_number == "DERM-401")
        gral_room = next(cr for cr in consultation_rooms if cr.room_number == "GRAL-101")
        gine_room = next(cr for cr in consultation_rooms if cr.room_number == "GINE-402")
        trau_room = next(cr for cr in consultation_rooms if cr.room_number == "TRAU-501")
        
        sample_appointments = [
            # Appointment 1: Juan Pérez - Cardiología - Next Monday 8:00 AM
            Appointment(
                patient_id=patients[0].id,
                specialty_id=specialties[1].id,  # Cardiología
                consultation_room_id=card_room.id,
                appointment_date=next_monday,
                start_time=time(8, 0),
                end_time=time(8, 20),
                shift=ShiftType.MORNING,
                reason="Control de presión arterial",
                status=AppointmentStatus.CONFIRMED
            ),
            # Appointment 2: María González - Dermatología - Next Monday 9:00 AM
            Appointment(
                patient_id=patients[1].id,
                specialty_id=specialties[3].id,  # Dermatología
                consultation_room_id=derm_room.id,
                appointment_date=next_monday,
                start_time=time(9, 0),
                end_time=time(9, 20),
                shift=ShiftType.MORNING,
                reason="Consulta por dermatitis",
                status=AppointmentStatus.PENDING
            ),
            # Appointment 3: Pedro Rodríguez - Medicina General - Next Tuesday 2:00 PM
            Appointment(
                patient_id=patients[2].id,
                specialty_id=specialties[0].id,  # Medicina General
                consultation_room_id=gral_room.id,
                appointment_date=next_monday + timedelta(days=1),
                start_time=time(14, 0),
                end_time=time(14, 20),
                shift=ShiftType.AFTERNOON,
                reason="Chequeo médico general",
                status=AppointmentStatus.PENDING
            ),
            # Appointment 4: Ana Martínez - Ginecología - Next Wednesday 10:00 AM
            Appointment(
                patient_id=patients[3].id,
                specialty_id=specialties[4].id,  # Ginecología
                consultation_room_id=gine_room.id,
                appointment_date=next_monday + timedelta(days=2),
                start_time=time(10, 0),
                end_time=time(10, 20),
                shift=ShiftType.MORNING,
                reason="Control anual",
                status=AppointmentStatus.CONFIRMED
            ),
            # Appointment 5: Carlos López - Traumatología - Next Thursday 3:00 PM
            Appointment(
                patient_id=patients[4].id,
                specialty_id=specialties[5].id,  # Traumatología
                consultation_room_id=trau_room.id,
                appointment_date=next_monday + timedelta(days=3),
                start_time=time(15, 0),
                end_time=time(15, 20),
                shift=ShiftType.AFTERNOON,
                reason="Dolor en rodilla izquierda",
                status=AppointmentStatus.PENDING
            ),
        ]
        
        db.add_all(sample_appointments)
        db.commit()
        print(f"   ✓ Created {len(sample_appointments)} sample appointments")
        
        # =====================================================
        # Summary
        # =====================================================
        print("\n" + "="*60)
        print("✅ DATABASE INITIALIZATION COMPLETED")
        print("="*60 + "\n")
        
        print("📊 SUMMARY:")
        print(f"   • Patients: {len(patients)}")
        print(f"   • Specialties: {len(specialties)}")
        print(f"   • Consultation Rooms: {len(consultation_rooms)}")
        print(f"   • Room Assignments: {assignment_count}")
        print(f"   • Sample Appointments: {len(sample_appointments)}")
        
        print("\n🔑 TEST CREDENTIALS:")
        print("   Document Number: 12345678")
        print("   Password: password123")
        
        print("\n⏰ SCHEDULE CONFIGURATION:")
        print("   • Morning: 8:00 AM - 1:00 PM (15 slots of 20 min)")
        print("   • Afternoon: 2:00 PM - 6:00 PM (12 slots of 20 min)")
        print("   • Working days: Monday to Friday")
        print("   • Slots: Generated dynamically (not pre-generated)")
        
        print("\n🎯 API ENDPOINTS:")
        print("   • GET  /consultation-rooms - List all rooms")
        print("   • GET  /consultation-rooms/by-specialty/{id} - Rooms by specialty")
        print("   • GET  /slots/available - Get available time slots")
        print("   • POST /appointments - Book an appointment")
        print("   • GET  /appointments/my-appointments - View your appointments")
        print("   • GET  /appointments/upcoming - View upcoming appointments")
        
        print("\n📖 DOCUMENTATION:")
        print("   • Swagger UI: http://localhost:3000/docs")
        print("   • ReDoc: http://localhost:3000/redoc")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error initializing database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🔧 Starting database initialization...")
    init_db()
    print("✨ Done!\n")
