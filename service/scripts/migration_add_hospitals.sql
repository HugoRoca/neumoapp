-- =====================================================
-- MIGRACIÓN: Agregar Tabla de Hospitales
-- =====================================================
-- Fecha: 2024-10-26
-- Descripción: 
--   - Crea tabla hospitals
--   - Modifica consultation_rooms para agregar hospital_id
--   - Actualiza datos existentes
-- =====================================================

BEGIN;

-- =====================================================
-- PASO 1: Crear tabla hospitals
-- =====================================================

CREATE TABLE IF NOT EXISTS hospitals (
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

COMMENT ON TABLE hospitals IS 'Hospitales del sistema';
COMMENT ON COLUMN hospitals.code IS 'Código único del hospital (ej: HOSP-01)';

RAISE NOTICE '✓ Tabla hospitals creada';


-- =====================================================
-- PASO 2: Insertar hospitales de ejemplo
-- =====================================================

INSERT INTO hospitals (name, code, address, district, city, phone, email, description, active) VALUES
('Hospital Central', 'HOSP-01', 'Av. Grau 1234', 'Cercado de Lima', 'Lima', '(01) 424-5678', 'info@hospitalcentral.pe', 'Hospital principal con todas las especialidades', true),
('Clínica San Pablo', 'HOSP-02', 'Av. El Polo 789', 'Surco', 'Lima', '(01) 610-7777', 'contacto@sanpablo.pe', 'Clínica privada especializada', true),
('Hospital Regional Norte', 'HOSP-03', 'Av. Túpac Amaru 456', 'Independencia', 'Lima', '(01) 533-2020', 'info@hospitalregional.gob.pe', 'Hospital público del cono norte', true);

RAISE NOTICE '✓ 3 hospitales insertados';


-- =====================================================
-- PASO 3: Modificar tabla consultation_rooms
-- =====================================================

-- Agregar columna hospital_id (temporalmente nullable)
ALTER TABLE consultation_rooms 
ADD COLUMN IF NOT EXISTS hospital_id INTEGER;

RAISE NOTICE '✓ Columna hospital_id agregada a consultation_rooms';


-- =====================================================
-- PASO 4: Asignar consultorios a hospitales
-- =====================================================

DO $$
DECLARE
    hospital_central_id INTEGER;
    hospital_san_pablo_id INTEGER;
    hospital_regional_id INTEGER;
BEGIN
    -- Obtener IDs de hospitales
    SELECT id INTO hospital_central_id FROM hospitals WHERE code = 'HOSP-01';
    SELECT id INTO hospital_san_pablo_id FROM hospitals WHERE code = 'HOSP-02';
    SELECT id INTO hospital_regional_id FROM hospitals WHERE code = 'HOSP-03';
    
    -- Distribuir consultorios entre hospitales
    -- Hospital Central: todos los consultorios de Edificio A
    UPDATE consultation_rooms 
    SET hospital_id = hospital_central_id
    WHERE building = 'Edificio A';
    
    -- Clínica San Pablo: todos los consultorios de Edificio B
    UPDATE consultation_rooms 
    SET hospital_id = hospital_san_pablo_id
    WHERE building = 'Edificio B';
    
    -- Hospital Regional Norte: crear nuevos consultorios
    INSERT INTO consultation_rooms (room_number, name, floor, building, hospital_id, description, active) VALUES
    ('GRAL-NORTE-01', 'Consultorio Medicina General Norte', '1', 'Edificio Principal', hospital_regional_id, 'Consultorio general', true),
    ('CARD-NORTE-01', 'Consultorio Cardiología Norte', '2', 'Edificio Principal', hospital_regional_id, 'Consultorio cardiológico', true);
    
    -- Asignar especialidades a los nuevos consultorios
    INSERT INTO specialty_consultation_rooms (specialty_id, consultation_room_id)
    SELECT 1, id FROM consultation_rooms WHERE room_number = 'GRAL-NORTE-01'
    UNION ALL
    SELECT 2, id FROM consultation_rooms WHERE room_number = 'CARD-NORTE-01';
    
    RAISE NOTICE '✓ Consultorios asignados a hospitales';
END $$;


-- =====================================================
-- PASO 5: Hacer hospital_id obligatorio
-- =====================================================

ALTER TABLE consultation_rooms 
ALTER COLUMN hospital_id SET NOT NULL;

ALTER TABLE consultation_rooms 
ADD CONSTRAINT fk_consultation_rooms_hospital 
FOREIGN KEY (hospital_id) 
REFERENCES hospitals(id) 
ON DELETE RESTRICT;

CREATE INDEX IF NOT EXISTS idx_consultation_rooms_hospital 
ON consultation_rooms(hospital_id);

RAISE NOTICE '✓ Constraints agregados';


-- =====================================================
-- PASO 6: Crear trigger para updated_at en hospitals
-- =====================================================

CREATE TRIGGER update_hospitals_updated_at 
BEFORE UPDATE ON hospitals 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

RAISE NOTICE '✓ Trigger creado';


-- =====================================================
-- PASO 7: Eliminar vistas existentes
-- =====================================================

DROP VIEW IF EXISTS v_consultation_rooms_with_specialties CASCADE;
DROP VIEW IF EXISTS v_specialties_with_rooms CASCADE;
DROP VIEW IF EXISTS v_upcoming_appointments CASCADE;

RAISE NOTICE '✓ Vistas antiguas eliminadas';


-- =====================================================
-- PASO 8: Crear vistas útiles
-- =====================================================

-- Vista: Hospitales con estadísticas
CREATE OR REPLACE VIEW v_hospitals_with_stats AS
SELECT 
    h.id,
    h.name,
    h.code,
    h.district,
    h.city,
    h.active,
    COUNT(DISTINCT cr.id) as total_rooms,
    COUNT(DISTINCT scr.specialty_id) as total_specialties,
    COUNT(DISTINCT a.id) as total_appointments
FROM hospitals h
LEFT JOIN consultation_rooms cr ON h.id = cr.hospital_id AND cr.active = true
LEFT JOIN specialty_consultation_rooms scr ON cr.id = scr.consultation_room_id
LEFT JOIN appointments a ON cr.id = a.consultation_room_id AND a.appointment_date >= CURRENT_DATE
WHERE h.active = true
GROUP BY h.id, h.name, h.code, h.district, h.city, h.active;

COMMENT ON VIEW v_hospitals_with_stats IS 'Hospitales con estadísticas de consultorios, especialidades y citas';

-- Vista: Consultorios con hospital (recreada con nuevas columnas)
CREATE VIEW v_consultation_rooms_with_specialties AS
SELECT 
    cr.id as room_id,
    cr.room_number,
    cr.name as room_name,
    cr.floor,
    cr.building,
    cr.hospital_id,
    h.name as hospital_name,
    h.code as hospital_code,
    cr.active,
    STRING_AGG(s.name, ', ' ORDER BY s.name) as specialties,
    COUNT(DISTINCT s.id) as specialty_count
FROM consultation_rooms cr
JOIN hospitals h ON cr.hospital_id = h.id
LEFT JOIN specialty_consultation_rooms scr ON cr.id = scr.consultation_room_id
LEFT JOIN specialties s ON scr.specialty_id = s.id
GROUP BY cr.id, cr.room_number, cr.name, cr.floor, cr.building, cr.hospital_id, h.name, h.code, cr.active;

COMMENT ON VIEW v_consultation_rooms_with_specialties IS 'Consultorios con hospital y especialidades asignadas';

RAISE NOTICE '✓ Vista v_consultation_rooms_with_specialties creada';


-- Vista: Especialidades con consultorios (recreada)
CREATE VIEW v_specialties_with_rooms AS
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

RAISE NOTICE '✓ Vista v_specialties_with_rooms creada';


-- Vista: Próximas citas (recreada con información de hospital)
CREATE VIEW v_upcoming_appointments AS
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
    cr.hospital_id,
    h.name as hospital_name,
    h.code as hospital_code,
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
JOIN hospitals h ON cr.hospital_id = h.id
WHERE a.appointment_date >= CURRENT_DATE
AND a.status IN ('pending', 'confirmed')
ORDER BY a.appointment_date, a.start_time;

COMMENT ON VIEW v_upcoming_appointments IS 'Próximas citas con información completa incluyendo hospital';

RAISE NOTICE '✓ Vista v_upcoming_appointments creada';
RAISE NOTICE '✓ Todas las vistas creadas exitosamente';


-- =====================================================
-- VERIFICACIÓN FINAL
-- =====================================================

DO $$
DECLARE
    hospital_count INTEGER;
    room_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO hospital_count FROM hospitals WHERE active = true;
    SELECT COUNT(*) INTO room_count FROM consultation_rooms WHERE active = true;
    
    RAISE NOTICE '';
    RAISE NOTICE '📊 ESTADÍSTICAS DE MIGRACIÓN:';
    RAISE NOTICE '  • Hospitales: %', hospital_count;
    RAISE NOTICE '  • Consultorios: %', room_count;
    RAISE NOTICE '';
END $$;

COMMIT;

-- =====================================================
-- RESUMEN
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '================================================';
    RAISE NOTICE '✅ MIGRACIÓN COMPLETADA EXITOSAMENTE';
    RAISE NOTICE '================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'CAMBIOS REALIZADOS:';
    RAISE NOTICE '  1. ✓ Tabla hospitals creada';
    RAISE NOTICE '  2. ✓ 3 hospitales insertados';
    RAISE NOTICE '  3. ✓ Campo hospital_id agregado a consultation_rooms';
    RAISE NOTICE '  4. ✓ Consultorios asignados a hospitales';
    RAISE NOTICE '  5. ✓ Constraints y triggers configurados';
    RAISE NOTICE '  6. ✓ Vistas antiguas eliminadas';
    RAISE NOTICE '  7. ✓ Vistas recreadas con información de hospital';
    RAISE NOTICE '';
    RAISE NOTICE 'NUEVA JERARQUÍA:';
    RAISE NOTICE '  Hospital → Consultation Rooms → Specialties';
    RAISE NOTICE '';
    RAISE NOTICE 'VERIFICAR MIGRACIÓN:';
    RAISE NOTICE '  SELECT * FROM v_hospitals_with_stats;';
    RAISE NOTICE '';
END $$;

