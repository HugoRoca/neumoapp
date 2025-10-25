-- =====================================================
-- DATOS DE PRUEBA - Sistema de Citas Médicas
-- =====================================================
-- Versión: 1.0 - Octubre 2024
-- Descripción: Datos de ejemplo para testing y demostración
-- Nota: Las especialidades y consultorios ya están en database_schema.sql
-- =====================================================

-- =====================================================
-- PACIENTES (20 pacientes de prueba)
-- =====================================================

-- Nota: Las contraseñas están hasheadas con bcrypt (SHA256 + bcrypt)
-- Todas las contraseñas son: "password123"
-- Hash generado: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy

INSERT INTO patients (document_number, lastname, firstname, date_birth, gender, address, phone, email, civil_status, password_hash, active) VALUES
-- Pacientes 1-5
('12345678', 'Pérez', 'Juan', '1985-05-15', 'Masculino', 'Av. Los Álamos 123, Lima', '987654321', 'juan.perez@email.com', 'Casado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('87654321', 'González', 'María', '1990-08-22', 'Femenino', 'Jr. Las Flores 456, Lima', '965432187', 'maria.gonzalez@email.com', 'Soltera', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('11111111', 'Rodríguez', 'Pedro', '1978-03-10', 'Masculino', 'Calle Los Pinos 789, Miraflores', '912345678', 'pedro.rodriguez@email.com', 'Casado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('22222222', 'Martínez', 'Ana', '1995-11-30', 'Femenino', 'Av. Arequipa 321, Lima', '923456789', 'ana.martinez@email.com', 'Soltera', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('33333333', 'López', 'Carlos', '1982-07-18', 'Masculino', 'Jr. Junín 654, San Isidro', '934567890', 'carlos.lopez@email.com', 'Divorciado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),

-- Pacientes 6-10
('44444444', 'Fernández', 'Laura', '1988-12-05', 'Femenino', 'Av. Javier Prado 987, San Borja', '945678901', 'laura.fernandez@email.com', 'Casada', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('55555555', 'Sánchez', 'Roberto', '1975-09-14', 'Masculino', 'Calle Real 234, Surco', '956789012', 'roberto.sanchez@email.com', 'Casado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('66666666', 'Torres', 'Carmen', '1992-04-20', 'Femenino', 'Jr. Lima 567, Pueblo Libre', '967890123', 'carmen.torres@email.com', 'Soltera', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('77777777', 'Ramírez', 'Diego', '1980-06-08', 'Masculino', 'Av. Brasil 890, Magdalena', '978901234', 'diego.ramirez@email.com', 'Casado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('88888888', 'Flores', 'Patricia', '1987-01-25', 'Femenino', 'Calle Lima 123, Barranco', '989012345', 'patricia.flores@email.com', 'Divorciada', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),

-- Pacientes 11-15
('99999999', 'Vega', 'Miguel', '1983-10-12', 'Masculino', 'Av. Colonial 456, Callao', '990123456', 'miguel.vega@email.com', 'Casado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('10101010', 'Castro', 'Sofía', '1994-02-28', 'Femenino', 'Jr. Ucayali 789, Cercado', '901234567', 'sofia.castro@email.com', 'Soltera', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('20202020', 'Ríos', 'Fernando', '1979-08-17', 'Masculino', 'Av. Venezuela 321, Lima', '912345670', 'fernando.rios@email.com', 'Casado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('30303030', 'Morales', 'Valentina', '1991-05-03', 'Femenino', 'Calle Bolívar 654, Jesús María', '923456780', 'valentina.morales@email.com', 'Soltera', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('40404040', 'Gutiérrez', 'Andrés', '1986-11-21', 'Masculino', 'Av. Garcilaso 987, Lince', '934567801', 'andres.gutierrez@email.com', 'Divorciado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),

-- Pacientes 16-20
('50505050', 'Mendoza', 'Isabella', '1993-07-09', 'Femenino', 'Jr. Huancayo 234, Breña', '945678012', 'isabella.mendoza@email.com', 'Casada', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('60606060', 'Rojas', 'Sebastián', '1981-03-16', 'Masculino', 'Av. Petit Thouars 567, Santa Beatriz', '956789023', 'sebastian.rojas@email.com', 'Casado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('70707070', 'Vargas', 'Camila', '1989-12-11', 'Femenino', 'Calle Independencia 890, Rímac', '967890134', 'camila.vargas@email.com', 'Soltera', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('80808080', 'Herrera', 'Mateo', '1984-09-04', 'Masculino', 'Jr. Carabaya 123, Cercado', '978901245', 'mateo.herrera@email.com', 'Casado', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true),
('90909090', 'Silva', 'Lucía', '1996-04-27', 'Femenino', 'Av. Alfonso Ugarte 456, Lima', '989012356', 'lucia.silva@email.com', 'Soltera', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5hhfCEinDC3Fy', true);


-- =====================================================
-- CITAS MÉDICAS (30 citas de ejemplo)
-- =====================================================

-- Función auxiliar para calcular fechas dinámicamente
DO $$
DECLARE
    next_monday DATE;
    base_date DATE;
BEGIN
    -- Calcular próximo lunes
    base_date := CURRENT_DATE;
    next_monday := base_date + ((8 - EXTRACT(DOW FROM base_date)::INTEGER) % 7)::INTEGER;
    
    -- Si hoy es lunes, usar hoy
    IF EXTRACT(DOW FROM base_date) = 1 THEN
        next_monday := base_date;
    END IF;
    
    -- Citas para la Semana 1 (Lunes a Viernes)
    
    -- LUNES - Semana 1
    INSERT INTO appointments (patient_id, specialty_id, consultation_room_id, appointment_date, start_time, end_time, shift, status, reason) VALUES
    (1, 2, 4, next_monday, '08:00:00', '08:20:00', 'morning', 'confirmed', 'Control de presión arterial y revisión de medicación'),
    (2, 4, 8, next_monday, '08:20:00', '08:40:00', 'morning', 'confirmed', 'Consulta por dermatitis en brazos'),
    (3, 1, 1, next_monday, '09:00:00', '09:20:00', 'morning', 'pending', 'Chequeo médico general anual'),
    (4, 5, 9, next_monday, '10:00:00', '10:20:00', 'morning', 'confirmed', 'Control ginecológico anual'),
    (5, 6, 10, next_monday, '14:00:00', '14:20:00', 'afternoon', 'pending', 'Dolor en rodilla izquierda tras caída'),
    (6, 3, 6, next_monday, '15:00:00', '15:20:00', 'afternoon', 'confirmed', 'Control pediátrico de rutina');
    
    -- MARTES - Semana 1
    INSERT INTO appointments (patient_id, specialty_id, consultation_room_id, appointment_date, start_time, end_time, shift, status, reason) VALUES
    (7, 2, 5, next_monday + 1, '08:00:00', '08:20:00', 'morning', 'confirmed', 'Seguimiento de arritmia cardíaca'),
    (8, 7, 12, next_monday + 1, '09:00:00', '09:20:00', 'morning', 'pending', 'Revisión de vista y actualización de lentes'),
    (9, 1, 2, next_monday + 1, '10:00:00', '10:20:00', 'morning', 'confirmed', 'Consulta por gripe y tos persistente'),
    (10, 8, 13, next_monday + 1, '11:00:00', '11:20:00', 'morning', 'pending', 'Consulta por migrañas frecuentes'),
    (11, 9, 14, next_monday + 1, '14:00:00', '14:20:00', 'afternoon', 'confirmed', 'Terapia de manejo de ansiedad'),
    (12, 1, 3, next_monday + 1, '15:00:00', '15:20:00', 'afternoon', 'pending', 'Consulta por dolor abdominal');
    
    -- MIÉRCOLES - Semana 1
    INSERT INTO appointments (patient_id, specialty_id, consultation_room_id, appointment_date, start_time, end_time, shift, status, reason) VALUES
    (13, 10, 16, next_monday + 2, '08:00:00', '08:20:00', 'morning', 'confirmed', 'Asesoramiento nutricional para pérdida de peso'),
    (14, 3, 7, next_monday + 2, '09:00:00', '09:20:00', 'morning', 'confirmed', 'Vacunación infantil programada'),
    (15, 4, 8, next_monday + 2, '10:00:00', '10:20:00', 'morning', 'pending', 'Consulta por acné y tratamiento'),
    (16, 6, 11, next_monday + 2, '11:00:00', '11:20:00', 'morning', 'confirmed', 'Fisioterapia de hombro'),
    (17, 9, 15, next_monday + 2, '14:00:00', '14:20:00', 'afternoon', 'pending', 'Consulta inicial de salud mental'),
    (18, 1, 1, next_monday + 2, '15:00:00', '15:20:00', 'afternoon', 'confirmed', 'Consulta por presión alta');
    
    -- JUEVES - Semana 1
    INSERT INTO appointments (patient_id, specialty_id, consultation_room_id, appointment_date, start_time, end_time, shift, status, reason) VALUES
    (19, 2, 4, next_monday + 3, '08:00:00', '08:20:00', 'morning', 'confirmed', 'Electrocardiograma de rutina'),
    (20, 5, 9, next_monday + 3, '09:00:00', '09:20:00', 'morning', 'pending', 'Consulta prenatal - primer trimestre'),
    (1, 7, 12, next_monday + 3, '10:00:00', '10:20:00', 'morning', 'confirmed', 'Revisión de cataratas'),
    (2, 10, 16, next_monday + 3, '11:00:00', '11:20:00', 'morning', 'pending', 'Plan nutricional para diabetes'),
    (3, 6, 10, next_monday + 3, '14:00:00', '14:20:00', 'afternoon', 'confirmed', 'Seguimiento de fractura de muñeca'),
    (4, 1, 2, next_monday + 3, '15:00:00', '15:20:00', 'afternoon', 'pending', 'Renovación de recetas médicas');
    
    -- VIERNES - Semana 1
    INSERT INTO appointments (patient_id, specialty_id, consultation_room_id, appointment_date, start_time, end_time, shift, status, reason) VALUES
    (5, 8, 13, next_monday + 4, '08:00:00', '08:20:00', 'morning', 'confirmed', 'Consulta neurológica por mareos'),
    (6, 3, 6, next_monday + 4, '09:00:00', '09:20:00', 'morning', 'pending', 'Control de crecimiento infantil'),
    (7, 4, 8, next_monday + 4, '10:00:00', '10:20:00', 'morning', 'confirmed', 'Tratamiento para psoriasis'),
    (8, 9, 14, next_monday + 4, '11:00:00', '11:20:00', 'morning', 'confirmed', 'Terapia familiar'),
    (9, 1, 3, next_monday + 4, '14:00:00', '14:20:00', 'afternoon', 'pending', 'Examen médico para trabajo'),
    (10, 2, 5, next_monday + 4, '15:00:00', '15:20:00', 'afternoon', 'confirmed', 'Holter cardíaco - seguimiento');
    
    RAISE NOTICE '✅ 30 citas creadas para próximas 2 semanas';
    RAISE NOTICE '   Base date: %', next_monday;
END $$;


-- =====================================================
-- CITAS HISTÓRICAS (10 citas completadas/canceladas)
-- =====================================================

DO $$
DECLARE
    last_week DATE;
BEGIN
    last_week := CURRENT_DATE - 7;
    
    -- Citas de la semana pasada (completadas y canceladas)
    INSERT INTO appointments (patient_id, specialty_id, consultation_room_id, appointment_date, start_time, end_time, shift, status, reason, observations) VALUES
    (1, 1, 1, last_week, '08:00:00', '08:20:00', 'morning', 'completed', 'Consulta general', 'Paciente en buen estado. Se recomienda seguimiento en 6 meses.'),
    (2, 2, 4, last_week, '09:00:00', '09:20:00', 'morning', 'completed', 'Control cardiológico', 'Presión arterial controlada. Mantener medicación actual.'),
    (3, 3, 6, last_week, '10:00:00', '10:20:00', 'morning', 'cancelled', 'Vacunación', 'Cancelado por paciente - reprogramar'),
    (4, 4, 8, last_week, '14:00:00', '14:20:00', 'afternoon', 'completed', 'Consulta dermatológica', 'Se prescribió tratamiento tópico. Revisar en 2 semanas.'),
    (5, 5, 9, last_week, '15:00:00', '15:20:00', 'afternoon', 'completed', 'Control ginecológico', 'Exámenes dentro de parámetros normales.'),
    (6, 6, 10, last_week + 1, '08:00:00', '08:20:00', 'morning', 'completed', 'Traumatología', 'Fractura sanando correctamente. Continuar con fisioterapia.'),
    (7, 7, 12, last_week + 1, '09:00:00', '09:20:00', 'morning', 'cancelled', 'Oftalmología', 'No asistió a la cita'),
    (8, 8, 13, last_week + 2, '10:00:00', '10:20:00', 'morning', 'completed', 'Neurología', 'Se solicitó resonancia magnética. Próxima cita en 2 semanas.'),
    (9, 9, 14, last_week + 2, '14:00:00', '14:20:00', 'afternoon', 'completed', 'Psicología', 'Sesión productiva. Continuar con terapia semanal.'),
    (10, 10, 16, last_week + 3, '15:00:00', '15:20:00', 'afternoon', 'completed', 'Nutrición', 'Plan alimenticio entregado. Control en 1 mes.');
    
    RAISE NOTICE '✅ 10 citas históricas creadas';
END $$;


-- =====================================================
-- VERIFICACIÓN DE DATOS
-- =====================================================

DO $$
DECLARE
    patient_count INTEGER;
    appointment_count INTEGER;
    appointment_by_status RECORD;
BEGIN
    -- Contar pacientes
    SELECT COUNT(*) INTO patient_count FROM patients;
    
    -- Contar citas
    SELECT COUNT(*) INTO appointment_count FROM appointments;
    
    RAISE NOTICE '';
    RAISE NOTICE '================================================';
    RAISE NOTICE '✅ DATOS DE PRUEBA INSERTADOS EXITOSAMENTE';
    RAISE NOTICE '================================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 RESUMEN:';
    RAISE NOTICE '  • Pacientes: %', patient_count;
    RAISE NOTICE '  • Citas totales: %', appointment_count;
    RAISE NOTICE '';
    RAISE NOTICE '📋 CITAS POR ESTADO:';
    
    FOR appointment_by_status IN 
        SELECT status, COUNT(*) as count 
        FROM appointments 
        GROUP BY status 
        ORDER BY status
    LOOP
        RAISE NOTICE '  • %: %', INITCAP(appointment_by_status.status), appointment_by_status.count;
    END LOOP;
    
    RAISE NOTICE '';
    RAISE NOTICE '🔑 CREDENCIALES DE PRUEBA (todas con password: "password123"):';
    RAISE NOTICE '  • DNI: 12345678 - Juan Pérez';
    RAISE NOTICE '  • DNI: 87654321 - María González';
    RAISE NOTICE '  • DNI: 11111111 - Pedro Rodríguez';
    RAISE NOTICE '  • DNI: 22222222 - Ana Martínez';
    RAISE NOTICE '  • ... (16 pacientes más)';
    RAISE NOTICE '';
    RAISE NOTICE '📅 DISTRIBUCIÓN DE CITAS:';
    RAISE NOTICE '  • Próximas 2 semanas: 30 citas';
    RAISE NOTICE '  • Históricas (completadas/canceladas): 10 citas';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 PRÓXIMOS PASOS:';
    RAISE NOTICE '  1. Iniciar API: python main.py';
    RAISE NOTICE '  2. Login: POST /auth/login';
    RAISE NOTICE '  3. Ver citas: GET /appointments/my-appointments';
    RAISE NOTICE '';
END $$;


-- =====================================================
-- QUERIES ÚTILES PARA VERIFICACIÓN
-- =====================================================

-- Ver todas las citas programadas
-- SELECT * FROM v_upcoming_appointments;

-- Ver citas por paciente
-- SELECT p.firstname, p.lastname, COUNT(a.id) as total_appointments
-- FROM patients p
-- LEFT JOIN appointments a ON p.id = a.patient_id
-- GROUP BY p.id, p.firstname, p.lastname
-- ORDER BY total_appointments DESC;

-- Ver ocupación por consultorio
-- SELECT cr.room_number, cr.name, COUNT(a.id) as appointments
-- FROM consultation_rooms cr
-- LEFT JOIN appointments a ON cr.id = a.consultation_room_id
-- WHERE a.appointment_date >= CURRENT_DATE
-- GROUP BY cr.id, cr.room_number, cr.name
-- ORDER BY appointments DESC;

-- Ver citas por especialidad
-- SELECT s.name, COUNT(a.id) as appointments
-- FROM specialties s
-- LEFT JOIN appointments a ON s.id = a.specialty_id
-- WHERE a.appointment_date >= CURRENT_DATE
-- GROUP BY s.id, s.name
-- ORDER BY appointments DESC;

