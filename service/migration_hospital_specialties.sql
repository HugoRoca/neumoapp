-- =====================================================
-- MIGRACIÓN: Hospital -> Especialidades -> Consultorios
-- =====================================================
-- Este script crea la relación M:N entre hospitales y especialidades
-- Ahora el flujo es: Hospital -> Especialidades -> Consultorios
-- =====================================================

BEGIN;

-- PASO 1: Crear tabla de asociación hospital_specialties
-- =====================================================
CREATE TABLE IF NOT EXISTS hospital_specialties (
    hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    specialty_id INTEGER NOT NULL REFERENCES specialties(id) ON DELETE CASCADE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (hospital_id, specialty_id)
);

CREATE INDEX idx_hospital_specialties_hospital ON hospital_specialties(hospital_id);
CREATE INDEX idx_hospital_specialties_specialty ON hospital_specialties(specialty_id);

RAISE NOTICE '✓ Tabla hospital_specialties creada';

-- PASO 2: Asignar especialidades a hospitales
-- =====================================================
-- Asignamos todas las especialidades a todos los hospitales por defecto
-- En producción, esto debería ser más selectivo
INSERT INTO hospital_specialties (hospital_id, specialty_id, active)
SELECT h.id, s.id, true
FROM hospitals h
CROSS JOIN specialties s
WHERE h.active = true AND s.active = true
ON CONFLICT (hospital_id, specialty_id) DO NOTHING;

RAISE NOTICE '✓ Especialidades asignadas a hospitales';

-- PASO 3: Eliminar vistas existentes
-- =====================================================
DROP VIEW IF EXISTS v_upcoming_appointments CASCADE;
DROP VIEW IF EXISTS v_room_usage_stats CASCADE;
DROP VIEW IF EXISTS v_consultation_rooms_with_specialties CASCADE;
DROP VIEW IF EXISTS v_specialties_with_rooms CASCADE;
DROP VIEW IF EXISTS v_hospitals_with_stats CASCADE;

RAISE NOTICE '✓ Vistas antiguas eliminadas';

-- PASO 4: Crear nuevas vistas optimizadas
-- =====================================================

-- Vista: Hospitales con estadísticas y especialidades
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

-- Vista: Consultorios con hospital y especialidades
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

-- Vista: Citas próximas con toda la información
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

-- Vista: Estadísticas de uso de consultorios
CREATE VIEW v_room_usage_stats AS
SELECT 
    cr.id as room_id,
    cr.room_number,
    cr.name as room_name,
    h.name as hospital_name,
    COUNT(DISTINCT a.id) as total_appointments,
    COUNT(DISTINCT CASE WHEN a.status = 'COMPLETED' THEN a.id END) as completed_appointments,
    COUNT(DISTINCT CASE WHEN a.status = 'PENDING' THEN a.id END) as pending_appointments,
    COUNT(DISTINCT CASE WHEN a.appointment_date >= CURRENT_DATE THEN a.id END) as upcoming_appointments,
    COUNT(DISTINCT scr.specialty_id) as specialty_count
FROM consultation_rooms cr
JOIN hospitals h ON cr.hospital_id = h.id
LEFT JOIN appointments a ON cr.id = a.consultation_room_id
LEFT JOIN specialty_consultation_rooms scr ON cr.id = scr.consultation_room_id
WHERE cr.active = true
GROUP BY cr.id, cr.room_number, cr.name, h.name;

RAISE NOTICE '✓ Nuevas vistas creadas';

-- PASO 5: Crear función auxiliar para obtener especialidades de un hospital
-- =====================================================
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

RAISE NOTICE '✓ Función get_hospital_specialties creada';

-- PASO 6: Crear función para obtener consultorios disponibles
-- =====================================================
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

RAISE NOTICE '✓ Función get_available_rooms_for_specialty creada';

-- PASO 7: Verificación de datos
-- =====================================================
DO $$
DECLARE
    v_hospital_count INTEGER;
    v_specialty_count INTEGER;
    v_assignment_count INTEGER;
    v_room_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_hospital_count FROM hospitals WHERE active = true;
    SELECT COUNT(*) INTO v_specialty_count FROM specialties WHERE active = true;
    SELECT COUNT(*) INTO v_assignment_count FROM hospital_specialties;
    SELECT COUNT(*) INTO v_room_count FROM consultation_rooms WHERE active = true;
    
    RAISE NOTICE '===========================================';
    RAISE NOTICE 'VERIFICACIÓN DE MIGRACIÓN';
    RAISE NOTICE '===========================================';
    RAISE NOTICE 'Hospitales activos: %', v_hospital_count;
    RAISE NOTICE 'Especialidades activas: %', v_specialty_count;
    RAISE NOTICE 'Asignaciones hospital-especialidad: %', v_assignment_count;
    RAISE NOTICE 'Consultorios activos: %', v_room_count;
    RAISE NOTICE '===========================================';
    
    IF v_assignment_count = 0 THEN
        RAISE WARNING 'No hay especialidades asignadas a hospitales!';
    END IF;
END $$;

-- PASO 8: Ejemplo de consultas
-- =====================================================
-- Descomentar para ver ejemplos de uso:

-- Ver hospitales con sus estadísticas
-- SELECT * FROM v_hospitals_with_stats;

-- Ver especialidades de un hospital específico
-- SELECT * FROM get_hospital_specialties(1);

-- Ver consultorios disponibles para una especialidad en un hospital
-- SELECT * FROM get_available_rooms_for_specialty(1, 1);

-- Ver citas próximas con toda la información
-- SELECT * FROM v_upcoming_appointments LIMIT 10;

COMMIT;

RAISE NOTICE '✓✓✓ Migración completada exitosamente ✓✓✓';

