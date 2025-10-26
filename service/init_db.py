"""
Script to initialize the database with sample data
NEW VERSION: Hospital -> Specialties -> Consultation Rooms
"""
from datetime import date, time, timedelta
from app.database.base import SessionLocal, engine, Base
from app.models.patient import Patient
from app.models.specialty import Specialty
from app.models.hospital import Hospital
from app.models.consultation_room import ConsultationRoom
from app.models.appointment import Appointment
from app.core.security import get_password_hash


def init_db():
    """Initialize database with sample data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Patient).first() or db.query(Specialty).first() or db.query(Hospital).first():
            print("⚠️  Database already contains data. Will not reinitialize.")
            print("   To start fresh, drop the database and run again.")
            return
        
        print("\n" + "="*60)
        print("🚀 INITIALIZING DATABASE")
        print("   Hospital → Specialties → Consultation Rooms")
        print("="*60 + "\n")
        
        # =====================================================
        # 1. Create sample patients
        # =====================================================
        print("📝 Creating patients...")
        
        patients = [
            Patient(
                document_number="12345678",
                last_name="Pérez",
                first_name="Juan",
                birth_date=date(1985, 5, 15),
                gender="M",
                address="Av. Example 123, Lima",
                phone="987654321",
                email="juan.perez@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="87654321",
                last_name="González",
                first_name="María",
                birth_date=date(1990, 8, 22),
                gender="F",
                address="Jr. Sample 456, Lima",
                phone="912345678",
                email="maria.gonzalez@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="11111111",
                last_name="Rodríguez",
                first_name="Pedro",
                birth_date=date(1978, 3, 10),
                gender="M",
                address="Calle Test 789, Lima",
                phone="999888777",
                email="pedro.rodriguez@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="22222222",
                last_name="Martínez",
                first_name="Ana",
                birth_date=date(1995, 12, 5),
                gender="F",
                address="Av. Demo 321, Lima",
                phone="988777666",
                email="ana.martinez@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="33333333",
                last_name="López",
                first_name="Carlos",
                birth_date=date(1982, 7, 18),
                gender="M",
                address="Jr. Testing 555, Lima",
                phone="977666555",
                email="carlos.lopez@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="44444444",
                last_name="Torres",
                first_name="Sofía",
                birth_date=date(1992, 11, 30),
                gender="F",
                address="Av. Los Olivos 234, Lima",
                phone="966554433",
                email="sofia.torres@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="55555555",
                last_name="Ramírez",
                first_name="Luis",
                birth_date=date(1988, 4, 12),
                gender="M",
                address="Jr. Las Flores 567, Lima",
                phone="955443322",
                email="luis.ramirez@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="66666666",
                last_name="Flores",
                first_name="Carmen",
                birth_date=date(1975, 9, 8),
                gender="F",
                address="Calle San Martín 890, Lima",
                phone="944332211",
                email="carmen.flores@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="77777777",
                last_name="Castro",
                first_name="Miguel",
                birth_date=date(1998, 2, 14),
                gender="M",
                address="Av. Colonial 123, Lima",
                phone="933221100",
                email="miguel.castro@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="88888888",
                last_name="Vega",
                first_name="Patricia",
                birth_date=date(1986, 7, 25),
                gender="F",
                address="Jr. Junín 456, Lima",
                phone="922110099",
                email="patricia.vega@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="99999999",
                last_name="Silva",
                first_name="Roberto",
                birth_date=date(1980, 12, 3),
                gender="M",
                address="Av. Brasil 789, Lima",
                phone="911009988",
                email="roberto.silva@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="10101010",
                last_name="Morales",
                first_name="Elena",
                birth_date=date(1993, 6, 17),
                gender="F",
                address="Calle Lima 321, Lima",
                phone="900998877",
                email="elena.morales@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="20202020",
                last_name="Quispe",
                first_name="José",
                birth_date=date(1970, 1, 20),
                gender="M",
                address="Jr. Ayacucho 654, Lima",
                phone="899887766",
                email="jose.quispe@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="30303030",
                last_name="Díaz",
                first_name="Rosa",
                birth_date=date(1996, 10, 9),
                gender="F",
                address="Av. Arequipa 987, Lima",
                phone="888776655",
                email="rosa.diaz@example.com",
                password_hash=get_password_hash("password123")
            ),
            Patient(
                document_number="40404040",
                last_name="Vargas",
                first_name="Fernando",
                birth_date=date(1984, 3, 28),
                gender="M",
                address="Calle Real 147, Lima",
                phone="877665544",
                email="fernando.vargas@example.com",
                password_hash=get_password_hash("password123")
            ),
        ]
        
        db.add_all(patients)
        db.commit()
        print(f"   ✓ Created {len(patients)} patients")
        
        # =====================================================
        # 2. Create specialties
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
        
        # Refresh specialties to get IDs
        for s in specialties:
            db.refresh(s)
        
        # =====================================================
        # 3. Create hospitals
        # =====================================================
        print("\n🏨 Creating hospitals...")
        
        hospitals = [
            Hospital(
                name="Hospital Nacional Rebagliati",
                code="HNR",
                address="Av. Rebagliati 490, Jesús María",
                district="Jesús María",
                city="Lima",
                phone="01-2654901",
                email="contacto@rebagliati.gob.pe",
                description="Hospital de alta complejidad del seguro social"
            ),
            Hospital(
                name="Hospital Almenara",
                code="HAL",
                address="Av. Grau 800, La Victoria",
                district="La Victoria",
                city="Lima",
                phone="01-3241818",
                email="contacto@almenara.gob.pe",
                description="Centro de atención médica especializada"
            ),
            Hospital(
                name="Clínica San Felipe",
                code="CSF",
                address="Av. Gregorio Escobedo 650, Jesús María",
                district="Jesús María",
                city="Lima",
                phone="01-2199000",
                email="info@sanfelipe.com.pe",
                description="Clínica privada de alta tecnología"
            ),
        ]
        
        db.add_all(hospitals)
        db.commit()
        print(f"   ✓ Created {len(hospitals)} hospitals")
        
        # Refresh hospitals to get IDs
        for h in hospitals:
            db.refresh(h)
        
        # =====================================================
        # 4. Assign specialties to hospitals
        # =====================================================
        print("\n🔗 Assigning specialties to hospitals...")
        
        # Hospital Rebagliati (todas las especialidades)
        for specialty in specialties:
            hospitals[0].specialties.append(specialty)
        
        # Hospital Almenara (la mayoría de especialidades excepto Nutrición)
        for specialty in specialties[:9]:  # Todas excepto Nutrición
            hospitals[1].specialties.append(specialty)
        
        # Clínica San Felipe (especialidades selectas)
        for i in [0, 1, 3, 4, 6, 9]:  # General, Cardio, Derm, Gine, Ofta, Nutri
            hospitals[2].specialties.append(specialties[i])
        
        db.commit()
        
        specialty_count_rebagliati = len(hospitals[0].specialties)
        specialty_count_almenara = len(hospitals[1].specialties)
        specialty_count_sanfelipe = len(hospitals[2].specialties)
        
        print(f"   ✓ Hospital Rebagliati: {specialty_count_rebagliati} specialties")
        print(f"   ✓ Hospital Almenara: {specialty_count_almenara} specialties")
        print(f"   ✓ Clínica San Felipe: {specialty_count_sanfelipe} specialties")
        
        # =====================================================
        # 5. Create consultation rooms (assigned to hospitals)
        # =====================================================
        print("\n🏢 Creating consultation rooms...")
        
        # HOSPITAL REBAGLIATI - Consultorios
        rebagliati_rooms = [
            # Medicina General (3)
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-GRAL-101",
                name="Consultorio Medicina General 1",
                floor="1",
                building="Pabellón A"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-GRAL-102",
                name="Consultorio Medicina General 2",
                floor="1",
                building="Pabellón A"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-GRAL-103",
                name="Consultorio Medicina General 3",
                floor="1",
                building="Pabellón A"
            ),
            # Cardiología (2)
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-CARD-201",
                name="Consultorio Cardiología 1",
                floor="2",
                building="Pabellón A",
                description="Equipado con ECG"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-CARD-202",
                name="Consultorio Cardiología 2",
                floor="2",
                building="Pabellón A",
                description="Con monitor Holter"
            ),
            # Pediatría (2)
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-PED-301",
                name="Consultorio Pediatría 1",
                floor="3",
                building="Pabellón B"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-PED-302",
                name="Consultorio Pediatría 2",
                floor="3",
                building="Pabellón B"
            ),
            # Otras especialidades (1 cada una)
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-DERM-401",
                name="Consultorio Dermatología",
                floor="4",
                building="Pabellón B"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-GINE-402",
                name="Consultorio Ginecología",
                floor="4",
                building="Pabellón B"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-TRAU-501",
                name="Consultorio Traumatología",
                floor="5",
                building="Pabellón A"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-OFTA-601",
                name="Consultorio Oftalmología",
                floor="6",
                building="Pabellón A"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-NEUR-602",
                name="Consultorio Neurología",
                floor="6",
                building="Pabellón A"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-PSI-701",
                name="Consultorio Psicología",
                floor="7",
                building="Pabellón B"
            ),
            ConsultationRoom(
                hospital_id=hospitals[0].id,
                room_number="R-NUTR-703",
                name="Consultorio Nutrición",
                floor="7",
                building="Pabellón B"
            ),
        ]
        
        # HOSPITAL ALMENARA - Consultorios
        almenara_rooms = [
            ConsultationRoom(
                hospital_id=hospitals[1].id,
                room_number="A-GRAL-101",
                name="Consultorio General A",
                floor="1",
                building="Torre Médica"
            ),
            ConsultationRoom(
                hospital_id=hospitals[1].id,
                room_number="A-GRAL-102",
                name="Consultorio General B",
                floor="1",
                building="Torre Médica"
            ),
            ConsultationRoom(
                hospital_id=hospitals[1].id,
                room_number="A-CARD-201",
                name="Cardiología",
                floor="2",
                building="Torre Médica"
            ),
            ConsultationRoom(
                hospital_id=hospitals[1].id,
                room_number="A-PED-301",
                name="Pediatría",
                floor="3",
                building="Torre Médica"
            ),
            ConsultationRoom(
                hospital_id=hospitals[1].id,
                room_number="A-DERM-401",
                name="Dermatología",
                floor="4",
                building="Torre Médica"
            ),
            ConsultationRoom(
                hospital_id=hospitals[1].id,
                room_number="A-GINE-402",
                name="Ginecología",
                floor="4",
                building="Torre Médica"
            ),
            ConsultationRoom(
                hospital_id=hospitals[1].id,
                room_number="A-TRAU-501",
                name="Traumatología",
                floor="5",
                building="Torre Médica"
            ),
        ]
        
        # CLÍNICA SAN FELIPE - Consultorios
        sanfelipe_rooms = [
            ConsultationRoom(
                hospital_id=hospitals[2].id,
                room_number="SF-101",
                name="Consultorio 101",
                floor="1",
                building="Edificio Principal"
            ),
            ConsultationRoom(
                hospital_id=hospitals[2].id,
                room_number="SF-102",
                name="Consultorio 102",
                floor="1",
                building="Edificio Principal"
            ),
            ConsultationRoom(
                hospital_id=hospitals[2].id,
                room_number="SF-201",
                name="Consultorio 201",
                floor="2",
                building="Edificio Principal"
            ),
            ConsultationRoom(
                hospital_id=hospitals[2].id,
                room_number="SF-202",
                name="Consultorio 202",
                floor="2",
                building="Edificio Principal"
            ),
        ]
        
        all_rooms = rebagliati_rooms + almenara_rooms + sanfelipe_rooms
        db.add_all(all_rooms)
        db.commit()
        print(f"   ✓ Created {len(all_rooms)} consultation rooms")
        print(f"      - Hospital Rebagliati: {len(rebagliati_rooms)} rooms")
        print(f"      - Hospital Almenara: {len(almenara_rooms)} rooms")
        print(f"      - Clínica San Felipe: {len(sanfelipe_rooms)} rooms")
        
        # Refresh rooms to get IDs
        for room in all_rooms:
            db.refresh(room)
        
        # =====================================================
        # 6. Assign consultation rooms to specialties
        # =====================================================
        print("\n🔗 Assigning consultation rooms to specialties...")
        
        # Helper function to find room by number
        def find_room(room_number):
            return next(r for r in all_rooms if r.room_number == room_number)
        
        # Helper function to find specialty by name
        def find_specialty(specialty_name):
            return next(s for s in specialties if s.name == specialty_name)
        
        # HOSPITAL REBAGLIATI assignments
        assignments_rebagliati = {
            "Medicina General": ["R-GRAL-101", "R-GRAL-102", "R-GRAL-103"],
            "Cardiología": ["R-CARD-201", "R-CARD-202"],
            "Pediatría": ["R-PED-301", "R-PED-302"],
            "Dermatología": ["R-DERM-401"],
            "Ginecología": ["R-GINE-402"],
            "Traumatología": ["R-TRAU-501"],
            "Oftalmología": ["R-OFTA-601"],
            "Neurología": ["R-NEUR-602"],
            "Psicología": ["R-PSI-701"],
            "Nutrición": ["R-NUTR-703"],
        }
        
        # HOSPITAL ALMENARA assignments
        assignments_almenara = {
            "Medicina General": ["A-GRAL-101", "A-GRAL-102"],
            "Cardiología": ["A-CARD-201"],
            "Pediatría": ["A-PED-301"],
            "Dermatología": ["A-DERM-401"],
            "Ginecología": ["A-GINE-402"],
            "Traumatología": ["A-TRAU-501"],
        }
        
        # CLÍNICA SAN FELIPE assignments (multi-uso)
        assignments_sanfelipe = {
            "Medicina General": ["SF-101", "SF-102"],
            "Cardiología": ["SF-201"],
            "Dermatología": ["SF-202"],
            "Ginecología": ["SF-202"],
            "Oftalmología": ["SF-201"],
            "Nutrición": ["SF-101"],
        }
        
        assignment_count = 0
        
        for specialty_name, room_numbers in assignments_rebagliati.items():
            specialty = find_specialty(specialty_name)
            for room_number in room_numbers:
                room = find_room(room_number)
                specialty.consultation_rooms.append(room)
                assignment_count += 1
        
        for specialty_name, room_numbers in assignments_almenara.items():
            specialty = find_specialty(specialty_name)
            for room_number in room_numbers:
                room = find_room(room_number)
                specialty.consultation_rooms.append(room)
                assignment_count += 1
        
        for specialty_name, room_numbers in assignments_sanfelipe.items():
            specialty = find_specialty(specialty_name)
            for room_number in room_numbers:
                room = find_room(room_number)
                if room not in specialty.consultation_rooms:
                    specialty.consultation_rooms.append(room)
                    assignment_count += 1
        
        db.commit()
        print(f"   ✓ Created {assignment_count} specialty-room assignments")
        
        # =====================================================
        # 7. Create sample appointments
        # =====================================================
        print("\n📅 Creating sample appointments...")
        
        # Get dates for next week (week starting Monday 28/10/2024)
        # Since today is 26/10/2024 (Saturday), next Monday is 28/10/2024
        next_monday = date(2024, 10, 28)  # Monday
        next_tuesday = date(2024, 10, 29)  # Tuesday
        next_wednesday = date(2024, 10, 30)  # Wednesday
        next_thursday = date(2024, 10, 31)  # Thursday
        next_friday = date(2024, 11, 1)  # Friday
        
        sample_appointments = [
            # ==================== LUNES 28/10/2024 ====================
            # Mañana
            Appointment(
                patient_id=patients[0].id,
                specialty_id=find_specialty("Cardiología").id,
                consultation_room_id=find_room("R-CARD-201").id,
                appointment_date=next_monday,
                start_time=time(8, 0),
                end_time=time(8, 20),
                shift="morning",
                reason="Control de presión arterial",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[1].id,
                specialty_id=find_specialty("Medicina General").id,
                consultation_room_id=find_room("R-GRAL-101").id,
                appointment_date=next_monday,
                start_time=time(8, 20),
                end_time=time(8, 40),
                shift="morning",
                reason="Consulta por gripe",
                status="pending"
            ),
            Appointment(
                patient_id=patients[5].id,
                specialty_id=find_specialty("Pediatría").id,
                consultation_room_id=find_room("R-PED-301").id,
                appointment_date=next_monday,
                start_time=time(9, 0),
                end_time=time(9, 20),
                shift="morning",
                reason="Control de crecimiento",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[6].id,
                specialty_id=find_specialty("Dermatología").id,
                consultation_room_id=find_room("A-DERM-401").id,
                appointment_date=next_monday,
                start_time=time(10, 0),
                end_time=time(10, 20),
                shift="morning",
                reason="Consulta por dermatitis",
                status="pending"
            ),
            Appointment(
                patient_id=patients[7].id,
                specialty_id=find_specialty("Oftalmología").id,
                consultation_room_id=find_room("R-OFTA-601").id,
                appointment_date=next_monday,
                start_time=time(11, 0),
                end_time=time(11, 20),
                shift="morning",
                reason="Examen de vista",
                status="confirmed"
            ),
            # Tarde
            Appointment(
                patient_id=patients[8].id,
                specialty_id=find_specialty("Psicología").id,
                consultation_room_id=find_room("R-PSI-701").id,
                appointment_date=next_monday,
                start_time=time(14, 0),
                end_time=time(14, 20),
                shift="afternoon",
                reason="Terapia de seguimiento",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[9].id,
                specialty_id=find_specialty("Traumatología").id,
                consultation_room_id=find_room("R-TRAU-501").id,
                appointment_date=next_monday,
                start_time=time(15, 0),
                end_time=time(15, 20),
                shift="afternoon",
                reason="Dolor de espalda",
                status="pending"
            ),
            Appointment(
                patient_id=patients[10].id,
                specialty_id=find_specialty("Nutrición").id,
                consultation_room_id=find_room("R-NUTR-703").id,
                appointment_date=next_monday,
                start_time=time(16, 0),
                end_time=time(16, 20),
                shift="afternoon",
                reason="Plan nutricional",
                status="pending"
            ),
            
            # ==================== MARTES 29/10/2024 ====================
            # Mañana
            Appointment(
                patient_id=patients[2].id,
                specialty_id=find_specialty("Medicina General").id,
                consultation_room_id=find_room("SF-101").id,
                appointment_date=next_tuesday,
                start_time=time(8, 0),
                end_time=time(8, 20),
                shift="morning",
                reason="Chequeo médico general",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[11].id,
                specialty_id=find_specialty("Cardiología").id,
                consultation_room_id=find_room("R-CARD-202").id,
                appointment_date=next_tuesday,
                start_time=time(9, 0),
                end_time=time(9, 20),
                shift="morning",
                reason="Control post operatorio",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[12].id,
                specialty_id=find_specialty("Neurología").id,
                consultation_room_id=find_room("R-NEUR-602").id,
                appointment_date=next_tuesday,
                start_time=time(10, 0),
                end_time=time(10, 20),
                shift="morning",
                reason="Consulta por migrañas",
                status="pending"
            ),
            Appointment(
                patient_id=patients[13].id,
                specialty_id=find_specialty("Pediatría").id,
                consultation_room_id=find_room("A-PED-301").id,
                appointment_date=next_tuesday,
                start_time=time(11, 0),
                end_time=time(11, 20),
                shift="morning",
                reason="Vacunación",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[14].id,
                specialty_id=find_specialty("Ginecología").id,
                consultation_room_id=find_room("A-GINE-402").id,
                appointment_date=next_tuesday,
                start_time=time(12, 0),
                end_time=time(12, 20),
                shift="morning",
                reason="Control prenatal",
                status="confirmed"
            ),
            # Tarde
            Appointment(
                patient_id=patients[0].id,
                specialty_id=find_specialty("Medicina General").id,
                consultation_room_id=find_room("A-GRAL-101").id,
                appointment_date=next_tuesday,
                start_time=time(14, 0),
                end_time=time(14, 20),
                shift="afternoon",
                reason="Resultados de análisis",
                status="pending"
            ),
            Appointment(
                patient_id=patients[5].id,
                specialty_id=find_specialty("Dermatología").id,
                consultation_room_id=find_room("SF-202").id,
                appointment_date=next_tuesday,
                start_time=time(15, 0),
                end_time=time(15, 20),
                shift="afternoon",
                reason="Revisión de tratamiento",
                status="pending"
            ),
            
            # ==================== MIÉRCOLES 30/10/2024 ====================
            # Mañana
            Appointment(
                patient_id=patients[3].id,
                specialty_id=find_specialty("Ginecología").id,
                consultation_room_id=find_room("R-GINE-402").id,
                appointment_date=next_wednesday,
                start_time=time(8, 0),
                end_time=time(8, 20),
                shift="morning",
                reason="Control anual",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[6].id,
                specialty_id=find_specialty("Traumatología").id,
                consultation_room_id=find_room("A-TRAU-501").id,
                appointment_date=next_wednesday,
                start_time=time(9, 0),
                end_time=time(9, 20),
                shift="morning",
                reason="Terapia física",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[7].id,
                specialty_id=find_specialty("Cardiología").id,
                consultation_room_id=find_room("SF-201").id,
                appointment_date=next_wednesday,
                start_time=time(10, 0),
                end_time=time(10, 20),
                shift="morning",
                reason="Control de arritmia",
                status="pending"
            ),
            Appointment(
                patient_id=patients[8].id,
                specialty_id=find_specialty("Medicina General").id,
                consultation_room_id=find_room("R-GRAL-102").id,
                appointment_date=next_wednesday,
                start_time=time(11, 0),
                end_time=time(11, 20),
                shift="morning",
                reason="Dolor abdominal",
                status="pending"
            ),
            Appointment(
                patient_id=patients[9].id,
                specialty_id=find_specialty("Oftalmología").id,
                consultation_room_id=find_room("R-OFTA-601").id,
                appointment_date=next_wednesday,
                start_time=time(12, 0),
                end_time=time(12, 20),
                shift="morning",
                reason="Cambio de lentes",
                status="confirmed"
            ),
            # Tarde
            Appointment(
                patient_id=patients[10].id,
                specialty_id=find_specialty("Psicología").id,
                consultation_room_id=find_room("R-PSI-701").id,
                appointment_date=next_wednesday,
                start_time=time(14, 0),
                end_time=time(14, 20),
                shift="afternoon",
                reason="Consulta inicial",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[11].id,
                specialty_id=find_specialty("Nutrición").id,
                consultation_room_id=find_room("SF-101").id,
                appointment_date=next_wednesday,
                start_time=time(15, 0),
                end_time=time(15, 20),
                shift="afternoon",
                reason="Control de peso",
                status="pending"
            ),
            Appointment(
                patient_id=patients[12].id,
                specialty_id=find_specialty("Dermatología").id,
                consultation_room_id=find_room("R-DERM-401").id,
                appointment_date=next_wednesday,
                start_time=time(16, 0),
                end_time=time(16, 20),
                shift="afternoon",
                reason="Revisión de lunares",
                status="pending"
            ),
            
            # ==================== JUEVES 31/10/2024 ====================
            # Mañana
            Appointment(
                patient_id=patients[4].id,
                specialty_id=find_specialty("Traumatología").id,
                consultation_room_id=find_room("A-TRAU-501").id,
                appointment_date=next_thursday,
                start_time=time(8, 0),
                end_time=time(8, 20),
                shift="morning",
                reason="Dolor en rodilla izquierda",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[13].id,
                specialty_id=find_specialty("Medicina General").id,
                consultation_room_id=find_room("R-GRAL-103").id,
                appointment_date=next_thursday,
                start_time=time(9, 0),
                end_time=time(9, 20),
                shift="morning",
                reason="Fiebre persistente",
                status="pending"
            ),
            Appointment(
                patient_id=patients[14].id,
                specialty_id=find_specialty("Cardiología").id,
                consultation_room_id=find_room("A-CARD-201").id,
                appointment_date=next_thursday,
                start_time=time(10, 0),
                end_time=time(10, 20),
                shift="morning",
                reason="Electrocardiograma",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[1].id,
                specialty_id=find_specialty("Pediatría").id,
                consultation_room_id=find_room("R-PED-302").id,
                appointment_date=next_thursday,
                start_time=time(11, 0),
                end_time=time(11, 20),
                shift="morning",
                reason="Control de desarrollo",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[2].id,
                specialty_id=find_specialty("Neurología").id,
                consultation_room_id=find_room("R-NEUR-602").id,
                appointment_date=next_thursday,
                start_time=time(12, 0),
                end_time=time(12, 20),
                shift="morning",
                reason="Seguimiento neurológico",
                status="pending"
            ),
            # Tarde
            Appointment(
                patient_id=patients[3].id,
                specialty_id=find_specialty("Oftalmología").id,
                consultation_room_id=find_room("SF-201").id,
                appointment_date=next_thursday,
                start_time=time(14, 0),
                end_time=time(14, 20),
                shift="afternoon",
                reason="Control de presión ocular",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[4].id,
                specialty_id=find_specialty("Medicina General").id,
                consultation_room_id=find_room("SF-102").id,
                appointment_date=next_thursday,
                start_time=time(15, 0),
                end_time=time(15, 20),
                shift="afternoon",
                reason="Certificado médico",
                status="pending"
            ),
            Appointment(
                patient_id=patients[5].id,
                specialty_id=find_specialty("Ginecología").id,
                consultation_room_id=find_room("SF-202").id,
                appointment_date=next_thursday,
                start_time=time(16, 0),
                end_time=time(16, 20),
                shift="afternoon",
                reason="Papanicolau",
                status="confirmed"
            ),
            
            # ==================== VIERNES 01/11/2024 ====================
            # Mañana
            Appointment(
                patient_id=patients[6].id,
                specialty_id=find_specialty("Medicina General").id,
                consultation_room_id=find_room("A-GRAL-102").id,
                appointment_date=next_friday,
                start_time=time(8, 0),
                end_time=time(8, 20),
                shift="morning",
                reason="Chequeo preventivo",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[7].id,
                specialty_id=find_specialty("Psicología").id,
                consultation_room_id=find_room("R-PSI-701").id,
                appointment_date=next_friday,
                start_time=time(9, 0),
                end_time=time(9, 20),
                shift="morning",
                reason="Terapia de pareja",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[8].id,
                specialty_id=find_specialty("Dermatología").id,
                consultation_room_id=find_room("A-DERM-401").id,
                appointment_date=next_friday,
                start_time=time(10, 0),
                end_time=time(10, 20),
                shift="morning",
                reason="Tratamiento de acné",
                status="pending"
            ),
            Appointment(
                patient_id=patients[9].id,
                specialty_id=find_specialty("Cardiología").id,
                consultation_room_id=find_room("R-CARD-201").id,
                appointment_date=next_friday,
                start_time=time(11, 0),
                end_time=time(11, 20),
                shift="morning",
                reason="Holter de presión",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[10].id,
                specialty_id=find_specialty("Traumatología").id,
                consultation_room_id=find_room("R-TRAU-501").id,
                appointment_date=next_friday,
                start_time=time(12, 0),
                end_time=time(12, 20),
                shift="morning",
                reason="Dolor de hombro",
                status="pending"
            ),
            # Tarde
            Appointment(
                patient_id=patients[11].id,
                specialty_id=find_specialty("Medicina General").id,
                consultation_room_id=find_room("R-GRAL-101").id,
                appointment_date=next_friday,
                start_time=time(14, 0),
                end_time=time(14, 20),
                shift="afternoon",
                reason="Renovación de receta",
                status="pending"
            ),
            Appointment(
                patient_id=patients[12].id,
                specialty_id=find_specialty("Nutrición").id,
                consultation_room_id=find_room("R-NUTR-703").id,
                appointment_date=next_friday,
                start_time=time(15, 0),
                end_time=time(15, 20),
                shift="afternoon",
                reason="Dieta para diabéticos",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[13].id,
                specialty_id=find_specialty("Pediatría").id,
                consultation_room_id=find_room("A-PED-301").id,
                appointment_date=next_friday,
                start_time=time(16, 0),
                end_time=time(16, 20),
                shift="afternoon",
                reason="Control mensual",
                status="confirmed"
            ),
            Appointment(
                patient_id=patients[14].id,
                specialty_id=find_specialty("Ginecología").id,
                consultation_room_id=find_room("R-GINE-402").id,
                appointment_date=next_friday,
                start_time=time(17, 0),
                end_time=time(17, 20),
                shift="afternoon",
                reason="Ecografía",
                status="confirmed"
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
        print(f"   • Hospitals: {len(hospitals)}")
        print(f"   • Hospital-Specialty Assignments: {specialty_count_rebagliati + specialty_count_almenara + specialty_count_sanfelipe}")
        print(f"   • Consultation Rooms: {len(all_rooms)}")
        print(f"   • Specialty-Room Assignments: {assignment_count}")
        print(f"   • Sample Appointments: {len(sample_appointments)}")
        
        print("\n🏨 HOSPITALS:")
        print(f"   • {hospitals[0].name} ({hospitals[0].code}): {specialty_count_rebagliati} specialties, {len(rebagliati_rooms)} rooms")
        print(f"   • {hospitals[1].name} ({hospitals[1].code}): {specialty_count_almenara} specialties, {len(almenara_rooms)} rooms")
        print(f"   • {hospitals[2].name} ({hospitals[2].code}): {specialty_count_sanfelipe} specialties, {len(sanfelipe_rooms)} rooms")
        
        print("\n🔑 TEST CREDENTIALS:")
        print("   Document Numbers: 12345678, 87654321, 11111111, ..., 40404040")
        print("   Password (for all): password123")
        print("   Total patients: 15")
        
        print("\n⏰ SCHEDULE CONFIGURATION:")
        print("   • Morning: 8:00 AM - 1:00 PM (15 slots of 20 min)")
        print("   • Afternoon: 2:00 PM - 6:00 PM (12 slots of 20 min)")
        print("   • Working days: Monday to Friday")
        print("   • Slots: Generated dynamically (not pre-generated)")
        
        print("\n🎯 NEW BOOKING FLOW:")
        print("   1. GET  /hospitals → Select hospital")
        print("   2. GET  /hospitals/{id}/specialties → Select specialty")
        print("   3. GET  /slots/available?hospital_id=X&specialty_id=Y → Check slots")
        print("   4. POST /appointments → Book appointment")
        print("   5. GET  /appointments/my-appointments → View appointments")
        
        print("\n📖 DOCUMENTATION:")
        print("   • Swagger UI: http://localhost:3000/docs")
        print("   • ReDoc: http://localhost:3000/redoc")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🔧 Starting database initialization...")
    init_db()
    print("✨ Done!\n")
