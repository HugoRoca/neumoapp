-- =====================================================
-- MIGRACIÓN: Agregar Estado "rescheduled" a Appointments
-- =====================================================
-- Fecha: 2024-10-26
-- Descripción: 
--   - Actualiza el CHECK constraint de appointments.status
--   - Agrega "rescheduled" como estado válido
-- =====================================================

BEGIN;

-- =====================================================
-- PASO 1: Eliminar constraint existente
-- =====================================================

ALTER TABLE appointments 
DROP CONSTRAINT IF EXISTS check_status_valid;

-- =====================================================
-- PASO 2: Crear nuevo constraint con "rescheduled"
-- =====================================================

ALTER TABLE appointments 
ADD CONSTRAINT check_status_valid 
CHECK (status IN ('pending', 'confirmed', 'rescheduled', 'cancelled', 'completed'));

-- =====================================================
-- VERIFICACIÓN
-- =====================================================

-- Verificar que el constraint fue creado correctamente
DO $$
BEGIN
    RAISE NOTICE '✓ Constraint check_status_valid actualizado exitosamente';
    RAISE NOTICE '✓ Estados válidos ahora incluyen: pending, confirmed, rescheduled, cancelled, completed';
END $$;

COMMIT;

-- =====================================================
-- NOTAS
-- =====================================================
-- Este script actualiza el CHECK constraint para permitir
-- el estado "rescheduled" en la tabla appointments.
-- 
-- Estados disponibles:
--   - pending: Cita pendiente de confirmación
--   - confirmed: Cita confirmada
--   - rescheduled: Cita reprogramada (el slot original sigue ocupado)
--   - cancelled: Cita cancelada (el slot queda disponible)
--   - completed: Cita completada
-- =====================================================

