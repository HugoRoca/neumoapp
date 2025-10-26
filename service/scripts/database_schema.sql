-- =====================================================
-- ESQUEMA COMPLETO - Sistema de Citas Médicas
-- =====================================================
-- Versión: 4.0 - Octubre 2024
-- Descripción: Sistema completo con:
--   - Hospitales → Especialidades → Consultorios
--   - Relación M:N entre hospitales y especialidades
--   - Consultorios pertenecen a hospitales
--   - Horarios dinámicos, arquitectura limpia
-- =====================================================

-- Eliminar objetos si existen (para reinstalación limpia)
DROP VIEW IF EXISTS v_upcoming_appointments CASCADE;
DROP VIEW IF EXISTS v_room_usage_stats CASCADE;
DROP VIEW IF EXISTS v_consultation_rooms_with_info CASCADE;
DROP VIEW IF EXISTS v_hospital_specialties CASCADE;
DROP VIEW IF EXISTS v_hospitals_with_stats CASCADE;
DROP VIEW IF EXISTS v_specialties_with_rooms CASCADE;
DROP VIEW IF EXISTS v_consultation_rooms_with_specialties CASCADE;

DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS specialty_consultation_rooms CASCADE;
DROP TABLE IF EXISTS hospital_specialties CASCADE;
DROP TABLE IF EXISTS consultation_rooms CASCADE;
DROP TABLE IF EXISTS hospitals CASCADE;
DROP TABLE IF EXISTS specialties CASCADE;
DROP TABLE IF EXISTS patients CASCADE;

-- =====================================================
-- TABLA: patients (pacientes)
-- =====================================================
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR(20) UNIQUE NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F')) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE NOT NULL,
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
-- TABLA: hospitals (hospitales)
-- =====================================================
CREATE TABLE hospitals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    district VARCHAR(100),
    city VARCHAR(100) DEFAULT 'Lima',
    phone VARCHAR(20),
    email VARCHAR(100),
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hospitals_code ON hospitals(code);
CREATE INDEX idx_hospitals_active ON hospitals(active);
CREATE INDEX idx_hospitals_city ON hospitals(city);

COMMENT ON TABLE hospitals IS 'Hospitales/clínicas donde se brindan servicios';
COMMENT ON COLUMN hospitals.code IS 'Código único del hospital (ej: HNR, HAL)';


-- =====================================================
-- TABLA: hospital_specialties (relación M:N)
-- =====================================================
CREATE TABLE hospital_specialties (
    hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    specialty_id INTEGER NOT NULL REFERENCES specialties(id) ON DELETE CASCADE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (hospital_id, specialty_id)
);

CREATE INDEX idx_hospital_specialties_hospital ON hospital_specialties(hospital_id);
CREATE INDEX idx_hospital_specialties_specialty ON hospital_specialties(specialty_id);

COMMENT ON TABLE hospital_specialties IS 'Relación M:N entre hospitales y especialidades';
COMMENT ON COLUMN hospital_specialties.active IS 'Permite desactivar temporalmente una especialidad en un hospital';


-- =====================================================
-- TABLA: consultation_rooms (consultorios)
-- =====================================================
CREATE TABLE consultation_rooms (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE RESTRICT,
    room_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    floor VARCHAR(20),
    building VARCHAR(50),
    description VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consultation_rooms_hospital ON consultation_rooms(hospital_id);
CREATE INDEX idx_consultation_rooms_room_number ON consultation_rooms(room_number);
CREATE INDEX idx_consultation_rooms_active ON consultation_rooms(active);

COMMENT ON TABLE consultation_rooms IS 'Consultorios/salas de atención en hospitales';
COMMENT ON COLUMN consultation_rooms.hospital_id IS 'Hospital al que pertenece el consultorio';
COMMENT ON COLUMN consultation_rooms.room_number IS 'Código único del consultorio (ej: R-CARD-201)';


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


-- Función: Obtener especialidades de un hospital
CREATE OR REPLACE FUNCTION get_hospital_specialties(p_hospital_id INTEGER)
RETURNS TABLE (
    specialty_id INTEGER,
    specialty_name VARCHAR,
    specialty_description TEXT,
    available_rooms INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.name,
        s.description,
        COUNT(DISTINCT scr.consultation_room_id)::INTEGER
    FROM specialties s
    JOIN hospital_specialties hs ON s.id = hs.specialty_id
    LEFT JOIN consultation_rooms cr ON cr.hospital_id = hs.hospital_id AND cr.active = true
    LEFT JOIN specialty_consultation_rooms scr ON s.id = scr.specialty_id AND cr.id = scr.consultation_room_id
    WHERE hs.hospital_id = p_hospital_id 
      AND hs.active = true 
      AND s.active = true
    GROUP BY s.id, s.name, s.description
    ORDER BY s.name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_hospital_specialties IS 'Retorna las especialidades ofrecidas por un hospital';


-- Función: Obtener consultorios disponibles para especialidad en hospital
CREATE OR REPLACE FUNCTION get_available_rooms_for_specialty(
    p_hospital_id INTEGER,
    p_specialty_id INTEGER
)
RETURNS TABLE (
    room_id INTEGER,
    room_number VARCHAR,
    room_name VARCHAR,
    floor VARCHAR,
    building VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cr.id,
        cr.room_number,
        cr.name,
        cr.floor,
        cr.building
    FROM consultation_rooms cr
    JOIN specialty_consultation_rooms scr ON cr.id = scr.consultation_room_id
    WHERE cr.hospital_id = p_hospital_id
      AND scr.specialty_id = p_specialty_id
      AND cr.active = true
    ORDER BY cr.room_number;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_available_rooms_for_specialty IS 'Retorna consultorios disponibles para una especialidad en un hospital';


-- =====================================================
-- TRIGGERS
-- =====================================================

CREATE TRIGGER update_patients_updated_at 
BEFORE UPDATE ON patients 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_specialties_updated_at 
BEFORE UPDATE ON specialties 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hospitals_updated_at 
BEFORE UPDATE ON hospitals 
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

-- Vista: Hospitales con estadísticas
CREATE VIEW v_hospitals_with_stats AS
SELECT 
    h.id,
    h.name,
    h.code,
    h.address,
    h.district,
    h.city,
    h.phone,
    h.email,
    h.active,
    h.created_at,
    COUNT(DISTINCT hs.specialty_id) as specialty_count,
    COUNT(DISTINCT cr.id) as room_count,
    COUNT(DISTINCT CASE WHEN a.appointment_date >= CURRENT_DATE THEN a.id END) as upcoming_appointments,
    STRING_AGG(DISTINCT s.name, ', ' ORDER BY s.name) as specialties
FROM hospitals h
LEFT JOIN hospital_specialties hs ON h.id = hs.hospital_id AND hs.active = true
LEFT JOIN specialties s ON hs.specialty_id = s.id AND s.active = true
LEFT JOIN consultation_rooms cr ON h.id = cr.hospital_id AND cr.active = true
LEFT JOIN appointments a ON cr.id = a.consultation_room_id
WHERE h.active = true
GROUP BY h.id, h.name, h.code, h.address, h.district, h.city, h.phone, h.email, h.active, h.created_at;

COMMENT ON VIEW v_hospitals_with_stats IS 'Hospitales con estadísticas agregadas';


-- Vista: Especialidades por hospital
CREATE VIEW v_hospital_specialties AS
SELECT 
    h.id as hospital_id,
    h.name as hospital_name,
    h.code as hospital_code,
    s.id as specialty_id,
    s.name as specialty_name,
    s.description as specialty_description,
    COUNT(DISTINCT scr.consultation_room_id) as available_rooms,
    hs.active as assignment_active
FROM hospitals h
JOIN hospital_specialties hs ON h.id = hs.hospital_id
JOIN specialties s ON hs.specialty_id = s.id
LEFT JOIN consultation_rooms cr ON h.id = cr.hospital_id AND cr.active = true
LEFT JOIN specialty_consultation_rooms scr ON s.id = scr.specialty_id AND cr.id = scr.consultation_room_id
WHERE h.active = true AND s.active = true
GROUP BY h.id, h.name, h.code, s.id, s.name, s.description, hs.active;

COMMENT ON VIEW v_hospital_specialties IS 'Especialidades disponibles por hospital';


-- Vista: Consultorios con información completa
CREATE VIEW v_consultation_rooms_with_info AS
SELECT 
    cr.id as room_id,
    cr.room_number,
    cr.name as room_name,
    cr.floor,
    cr.building,
    cr.active as room_active,
    h.id as hospital_id,
    h.name as hospital_name,
    h.code as hospital_code,
    COUNT(DISTINCT scr.specialty_id) as specialty_count,
    STRING_AGG(DISTINCT s.name, ', ' ORDER BY s.name) as specialties
FROM consultation_rooms cr
JOIN hospitals h ON cr.hospital_id = h.id
LEFT JOIN specialty_consultation_rooms scr ON cr.id = scr.consultation_room_id
LEFT JOIN specialties s ON scr.specialty_id = s.id AND s.active = true
WHERE cr.active = true AND h.active = true
GROUP BY cr.id, cr.room_number, cr.name, cr.floor, cr.building, cr.active, 
         h.id, h.name, h.code;

COMMENT ON VIEW v_consultation_rooms_with_info IS 'Consultorios con hospital y especialidades';


-- Vista: Próximas citas con información completa
CREATE VIEW v_upcoming_appointments AS
SELECT 
    a.id as appointment_id,
    a.appointment_date,
    a.start_time,
    a.end_time,
    a.shift,
    a.status,
    p.id as patient_id,
    p.first_name || ' ' || p.last_name as patient_name,
    p.document_number as patient_document,
    s.id as specialty_id,
    s.name as specialty_name,
    cr.id as room_id,
    cr.room_number,
    cr.name as room_name,
    h.id as hospital_id,
    h.name as hospital_name,
    h.code as hospital_code
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN specialties s ON a.specialty_id = s.id
JOIN consultation_rooms cr ON a.consultation_room_id = cr.id
JOIN hospitals h ON cr.hospital_id = h.id
WHERE a.appointment_date >= CURRENT_DATE
ORDER BY a.appointment_date, a.start_time;

COMMENT ON VIEW v_upcoming_appointments IS 'Citas próximas con información completa';


-- Vista: Estadísticas de uso de consultorios
CREATE VIEW v_room_usage_stats AS
SELECT 
    cr.id as room_id,
    cr.room_number,
    cr.name as room_name,
    h.name as hospital_name,
    COUNT(DISTINCT a.id) as total_appointments,
    COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) as completed_appointments,
    COUNT(DISTINCT CASE WHEN a.status = 'pending' THEN a.id END) as pending_appointments,
    COUNT(DISTINCT CASE WHEN a.appointment_date >= CURRENT_DATE THEN a.id END) as upcoming_appointments,
    COUNT(DISTINCT scr.specialty_id) as specialty_count
FROM consultation_rooms cr
JOIN hospitals h ON cr.hospital_id = h.id
LEFT JOIN appointments a ON cr.id = a.consultation_room_id
LEFT JOIN specialty_consultation_rooms scr ON cr.id = scr.consultation_room_id
WHERE cr.active = true
GROUP BY cr.id, cr.room_number, cr.name, h.name;

COMMENT ON VIEW v_room_usage_stats IS 'Estadísticas de uso de consultorios';


-- =====================================================
-- RESUMEN DEL ESQUEMA
-- =====================================================
SELECT '========================================' as "";
SELECT 'ESQUEMA DE BASE DE DATOS CREADO' as "";
SELECT '========================================' as "";
SELECT 'Versión: 4.0' as "";
SELECT 'Fecha: Octubre 2024' as "";
SELECT '========================================' as "";
SELECT 'Estructura:' as "";
SELECT '  Hospital → Especialidades → Consultorios' as "";
SELECT '  Pacientes → Citas → Consultorios' as "";
SELECT '========================================' as "";
SELECT 'Tablas principales:' as "";
SELECT '  - patients (pacientes)' as "";
SELECT '  - specialties (especialidades)' as "";
SELECT '  - hospitals (hospitales)' as "";
SELECT '  - hospital_specialties (M:N)' as "";
SELECT '  - consultation_rooms (consultorios)' as "";
SELECT '  - specialty_consultation_rooms (M:N)' as "";
SELECT '  - appointments (citas)' as "";
SELECT '========================================' as "";
SELECT 'Vistas creadas:' as "";
SELECT '  - v_hospitals_with_stats' as "";
SELECT '  - v_hospital_specialties' as "";
SELECT '  - v_consultation_rooms_with_info' as "";
SELECT '  - v_upcoming_appointments' as "";
SELECT '  - v_room_usage_stats' as "";
SELECT '========================================' as "";
