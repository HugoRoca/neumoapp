-- =====================================================
-- ESQUEMA COMPLETO - Sistema de Citas Médicas
-- =====================================================
-- Versión: 3.0 - Octubre 2024
-- Descripción: Sistema completo con consultorios (M:N), 
--              horarios dinámicos, y arquitectura limpia
-- =====================================================

-- Eliminar tablas si existen (para reinstalación limpia)
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS specialty_consultation_rooms CASCADE;
DROP TABLE IF EXISTS consultation_rooms CASCADE;
DROP TABLE IF EXISTS specialties CASCADE;
DROP TABLE IF EXISTS patients CASCADE;

-- =====================================================
-- TABLA: patients (pacientes)
-- =====================================================
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR(20) UNIQUE NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    date_birth DATE NOT NULL,
    gender VARCHAR(20) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    civil_status VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patients_document ON patients(document_number);
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_patients_active ON patients(active);

COMMENT ON TABLE patients IS 'Pacientes del sistema';
COMMENT ON COLUMN patients.document_number IS 'DNI o documento de identidad';
COMMENT ON COLUMN patients.password_hash IS 'Hash bcrypt de la contraseña';


-- =====================================================
-- TABLA: specialties (especialidades médicas)
-- =====================================================
CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_specialties_active ON specialties(active);
CREATE INDEX idx_specialties_name ON specialties(name);

COMMENT ON TABLE specialties IS 'Especialidades médicas disponibles';


-- =====================================================
-- TABLA: consultation_rooms (consultorios)
-- =====================================================
CREATE TABLE consultation_rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    floor VARCHAR(20),
    building VARCHAR(50),
    description VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consultation_rooms_room_number ON consultation_rooms(room_number);
CREATE INDEX idx_consultation_rooms_active ON consultation_rooms(active);

COMMENT ON TABLE consultation_rooms IS 'Consultorios/salas de atención';
COMMENT ON COLUMN consultation_rooms.room_number IS 'Código único del consultorio (ej: CARD-201)';


-- =====================================================
-- TABLA: specialty_consultation_rooms (relación M:N)
-- =====================================================
CREATE TABLE specialty_consultation_rooms (
    specialty_id INTEGER NOT NULL REFERENCES specialties(id) ON DELETE CASCADE,
    consultation_room_id INTEGER NOT NULL REFERENCES consultation_rooms(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (specialty_id, consultation_room_id)
);

CREATE INDEX idx_specialty_rooms_specialty ON specialty_consultation_rooms(specialty_id);
CREATE INDEX idx_specialty_rooms_room ON specialty_consultation_rooms(consultation_room_id);

COMMENT ON TABLE specialty_consultation_rooms IS 'Relación M:N entre especialidades y consultorios';


-- =====================================================
-- TABLA: appointments (citas médicas)
-- =====================================================
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    specialty_id INTEGER NOT NULL REFERENCES specialties(id) ON DELETE RESTRICT,
    consultation_room_id INTEGER NOT NULL REFERENCES consultation_rooms(id) ON DELETE RESTRICT,
    
    -- Datos de fecha/hora (sistema dinámico, sin tabla schedules)
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    shift VARCHAR(20) NOT NULL,
    
    -- Información adicional
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    reason TEXT,
    observations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT check_shift_valid CHECK (shift IN ('morning', 'afternoon')),
    CONSTRAINT check_end_time_after_start_time CHECK (end_time > start_time),
    CONSTRAINT check_status_valid CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed'))
);

CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_specialty ON appointments(specialty_id);
CREATE INDEX idx_appointments_consultation_room ON appointments(consultation_room_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_specialty_date ON appointments(specialty_id, appointment_date);
CREATE INDEX idx_appointments_room_date_time ON appointments(consultation_room_id, appointment_date, start_time);

COMMENT ON TABLE appointments IS 'Citas médicas agendadas';
COMMENT ON COLUMN appointments.shift IS 'Turno: morning (8-13h) o afternoon (14-18h)';
COMMENT ON COLUMN appointments.start_time IS 'Hora de inicio (slots de 20 minutos)';
COMMENT ON COLUMN appointments.end_time IS 'Hora de fin (automático: start_time + 20 min)';


-- =====================================================
-- FUNCIONES
-- =====================================================

-- Función: Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS 'Actualiza automáticamente el campo updated_at';


-- Función: Verificar disponibilidad de slot
CREATE OR REPLACE FUNCTION check_slot_availability(
    p_specialty_id INTEGER,
    p_appointment_date DATE,
    p_start_time TIME,
    p_shift VARCHAR(20),
    p_consultation_room_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    -- Verifica si ya existe una cita en ese slot
    SELECT EXISTS(
        SELECT 1 
        FROM appointments 
        WHERE specialty_id = p_specialty_id
        AND appointment_date = p_appointment_date
        AND start_time = p_start_time
        AND shift = p_shift
        AND consultation_room_id = p_consultation_room_id
        AND status IN ('pending', 'confirmed')
    ) INTO v_exists;
    
    RETURN NOT v_exists;  -- TRUE = disponible, FALSE = ocupado
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_slot_availability IS 'Verifica si un slot está disponible para agendar';


-- Función: Validar día laboral (lunes a viernes)
CREATE OR REPLACE FUNCTION is_weekday(check_date DATE) 
RETURNS BOOLEAN AS $$
BEGIN
    -- DOW: 0=domingo, 1=lunes, ..., 6=sábado
    RETURN EXTRACT(DOW FROM check_date) BETWEEN 1 AND 5;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION is_weekday IS 'Verifica si una fecha es día laboral (lunes-viernes)';


-- Función: Obtener consultorios de una especialidad
CREATE OR REPLACE FUNCTION get_specialty_rooms(p_specialty_id INTEGER)
RETURNS TABLE(
    room_id INTEGER,
    room_number VARCHAR(20),
    room_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cr.id,
        cr.room_number,
        cr.name
    FROM consultation_rooms cr
    JOIN specialty_consultation_rooms scr ON cr.id = scr.consultation_room_id
    WHERE scr.specialty_id = p_specialty_id
    AND cr.active = true
    ORDER BY cr.room_number;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_specialty_rooms IS 'Retorna los consultorios asignados a una especialidad';


-- =====================================================
-- TRIGGERS
-- =====================================================

CREATE TRIGGER update_patients_updated_at 
BEFORE UPDATE ON patients 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_specialties_updated_at 
BEFORE UPDATE ON specialties 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consultation_rooms_updated_at 
BEFORE UPDATE ON consultation_rooms 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at 
BEFORE UPDATE ON appointments 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- =====================================================
-- VISTAS
-- =====================================================

-- Vista: Consultorios con sus especialidades
CREATE OR REPLACE VIEW v_consultation_rooms_with_specialties AS
SELECT 
    cr.id as room_id,
    cr.room_number,
    cr.name as room_name,
    cr.floor,
    cr.building,
    cr.active,
    STRING_AGG(s.name, ', ' ORDER BY s.name) as specialties,
    COUNT(DISTINCT s.id) as specialty_count
FROM consultation_rooms cr
LEFT JOIN specialty_consultation_rooms scr ON cr.id = scr.consultation_room_id
LEFT JOIN specialties s ON scr.specialty_id = s.id
GROUP BY cr.id, cr.room_number, cr.name, cr.floor, cr.building, cr.active;

COMMENT ON VIEW v_consultation_rooms_with_specialties IS 'Consultorios con lista de especialidades asignadas';


-- Vista: Especialidades con sus consultorios
CREATE OR REPLACE VIEW v_specialties_with_rooms AS
SELECT 
    s.id as specialty_id,
    s.name as specialty_name,
    STRING_AGG(cr.room_number, ', ' ORDER BY cr.room_number) as rooms,
    COUNT(DISTINCT cr.id) as room_count
FROM specialties s
LEFT JOIN specialty_consultation_rooms scr ON s.id = scr.specialty_id
LEFT JOIN consultation_rooms cr ON scr.consultation_room_id = cr.id
WHERE s.active = true AND (cr.active = true OR cr.id IS NULL)
GROUP BY s.id, s.name;

COMMENT ON VIEW v_specialties_with_rooms IS 'Especialidades con lista de consultorios asignados';


-- Vista: Próximas citas (con info completa)
CREATE OR REPLACE VIEW v_upcoming_appointments AS
SELECT 
    a.id,
    a.patient_id,
    p.document_number,
    p.firstname || ' ' || p.lastname as patient_name,
    a.specialty_id,
    s.name as specialty_name,
    a.consultation_room_id,
    cr.room_number,
    cr.name as room_name,
    cr.floor,
    cr.building,
    a.appointment_date,
    a.start_time,
    a.end_time,
    a.shift,
    a.status,
    a.reason
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN specialties s ON a.specialty_id = s.id
JOIN consultation_rooms cr ON a.consultation_room_id = cr.id
WHERE a.appointment_date >= CURRENT_DATE
AND a.status IN ('pending', 'confirmed')
ORDER BY a.appointment_date, a.start_time;

COMMENT ON VIEW v_upcoming_appointments IS 'Próximas citas con información completa';


-- Vista: Estadísticas de uso de consultorios
CREATE OR REPLACE VIEW v_room_usage_stats AS
SELECT 
    cr.room_number,
    cr.name,
    cr.floor,
    cr.building,
    COUNT(a.id) as total_appointments,
    COUNT(CASE WHEN a.status = 'completed' THEN 1 END) as completed_appointments,
    COUNT(CASE WHEN a.status = 'cancelled' THEN 1 END) as cancelled_appointments,
    COUNT(CASE WHEN a.appointment_date >= CURRENT_DATE THEN 1 END) as upcoming_appointments
FROM consultation_rooms cr
LEFT JOIN appointments a ON cr.id = a.consultation_room_id
WHERE cr.active = true
GROUP BY cr.id, cr.room_number, cr.name, cr.floor, cr.building
ORDER BY total_appointments DESC;

COMMENT ON VIEW v_room_usage_stats IS 'Estadísticas de uso de consultorios';


-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Especialidades médicas
INSERT INTO specialties (name, description, active) VALUES
('Medicina General', 'Consulta general y diagnóstico inicial', true),
('Cardiología', 'Especialista en enfermedades del corazón', true),
('Pediatría', 'Atención médica para niños y adolescentes', true),
('Dermatología', 'Especialista en enfermedades de la piel', true),
('Ginecología', 'Salud reproductiva femenina', true),
('Traumatología', 'Especialista en lesiones del sistema músculo-esquelético', true),
('Oftalmología', 'Especialista en enfermedades de los ojos', true),
('Neurología', 'Especialista en el sistema nervioso', true),
('Psicología', 'Salud mental y bienestar emocional', true),
('Nutrición', 'Asesoramiento nutricional y dietético', true);


-- Consultorios (distribuidos en 2 edificios)
INSERT INTO consultation_rooms (room_number, name, floor, building, description, active) VALUES
-- Edificio A - Medicina General (3 consultorios)
('GRAL-101', 'Consultorio Medicina General 1', '1', 'Edificio A', 'Equipado para consultas generales', true),
('GRAL-102', 'Consultorio Medicina General 2', '1', 'Edificio A', 'Equipado para consultas generales', true),
('GRAL-103', 'Consultorio Medicina General 3', '1', 'Edificio A', 'Equipado para consultas generales', true),

-- Edificio A - Cardiología (2 consultorios)
('CARD-201', 'Consultorio Cardiología 1', '2', 'Edificio A', 'Equipado con ECG', true),
('CARD-202', 'Consultorio Cardiología 2', '2', 'Edificio A', 'Equipado con ECG y monitor Holter', true),

-- Edificio B - Pediatría (2 consultorios)
('PED-301', 'Consultorio Pediatría 1', '3', 'Edificio B', 'Ambiente infantil', true),
('PED-302', 'Consultorio Pediatría 2', '3', 'Edificio B', 'Ambiente infantil', true),

-- Edificio B - Dermatología (1 consultorio)
('DERM-401', 'Consultorio Dermatología', '4', 'Edificio B', 'Equipado con dermatoscopio', true),

-- Edificio B - Ginecología (1 consultorio)
('GINE-402', 'Consultorio Ginecología', '4', 'Edificio B', 'Equipado para consultas ginecológicas', true),

-- Edificio A - Traumatología (2 consultorios)
('TRAU-501', 'Consultorio Traumatología 1', '5', 'Edificio A', 'Equipado para evaluación musculoesquelética', true),
('TRAU-502', 'Consultorio Traumatología 2', '5', 'Edificio A', 'Equipado para evaluación musculoesquelética', true),

-- Edificio A - Oftalmología (1 consultorio)
('OFTA-601', 'Consultorio Oftalmología', '6', 'Edificio A', 'Equipado con oftalmoscopio y tonómetro', true),

-- Edificio A - Neurología (1 consultorio)
('NEUR-602', 'Consultorio Neurología', '6', 'Edificio A', 'Equipado para examen neurológico', true),

-- Edificio B - Psicología (2 consultorios)
('PSI-701', 'Consultorio Psicología 1', '7', 'Edificio B', 'Ambiente privado y confortable', true),
('PSI-702', 'Consultorio Psicología 2', '7', 'Edificio B', 'Ambiente privado y confortable', true),

-- Edificio B - Nutrición (1 consultorio)
('NUTR-703', 'Consultorio Nutrición', '7', 'Edificio B', 'Equipado con balanza y medidor de composición corporal', true);


-- Asignar consultorios a especialidades
INSERT INTO specialty_consultation_rooms (specialty_id, consultation_room_id) VALUES
-- Medicina General (id=1) -> GRAL-101, GRAL-102, GRAL-103
(1, 1), (1, 2), (1, 3),
-- Cardiología (id=2) -> CARD-201, CARD-202
(2, 4), (2, 5),
-- Pediatría (id=3) -> PED-301, PED-302
(3, 6), (3, 7),
-- Dermatología (id=4) -> DERM-401
(4, 8),
-- Ginecología (id=5) -> GINE-402
(5, 9),
-- Traumatología (id=6) -> TRAU-501, TRAU-502
(6, 10), (6, 11),
-- Oftalmología (id=7) -> OFTA-601
(7, 12),
-- Neurología (id=8) -> NEUR-602
(8, 13),
-- Psicología (id=9) -> PSI-701, PSI-702
(9, 14), (9, 15),
-- Nutrición (id=10) -> NUTR-703
(10, 16);


-- =====================================================
-- RESUMEN DE INSTALACIÓN
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '================================================';
    RAISE NOTICE '✅ ESQUEMA CREADO EXITOSAMENTE';
    RAISE NOTICE '================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'TABLAS CREADAS:';
    RAISE NOTICE '  • patients (pacientes)';
    RAISE NOTICE '  • specialties (especialidades)';
    RAISE NOTICE '  • consultation_rooms (consultorios)';
    RAISE NOTICE '  • specialty_consultation_rooms (relación M:N)';
    RAISE NOTICE '  • appointments (citas médicas)';
    RAISE NOTICE '';
    RAISE NOTICE 'DATOS INICIALES:';
    RAISE NOTICE '  • 10 especialidades médicas';
    RAISE NOTICE '  • 16 consultorios distribuidos en 2 edificios';
    RAISE NOTICE '  • Asignaciones automáticas';
    RAISE NOTICE '';
    RAISE NOTICE 'CARACTERÍSTICAS:';
    RAISE NOTICE '  • Horarios dinámicos (sin tabla schedules)';
    RAISE NOTICE '  • Turnos: Mañana (8-13h) / Tarde (14-18h)';
    RAISE NOTICE '  • Slots de 20 minutos (5 por hora)';
    RAISE NOTICE '  • Días laborales: Lunes a Viernes';
    RAISE NOTICE '  • Relación M:N entre especialidades y consultorios';
    RAISE NOTICE '';
    RAISE NOTICE 'PRÓXIMO PASO:';
    RAISE NOTICE '  Ejecutar: python init_db.py';
    RAISE NOTICE '  (Para crear pacientes de prueba y citas de ejemplo)';
    RAISE NOTICE '';
    RAISE NOTICE 'VERIFICAR:';
    RAISE NOTICE '  SELECT * FROM v_specialties_with_rooms;';
    RAISE NOTICE '  SELECT * FROM v_consultation_rooms_with_specialties;';
    RAISE NOTICE '';
END $$;
