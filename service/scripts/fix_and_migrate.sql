-- =====================================================
-- SCRIPT DE CORRECCIÓN Y MIGRACIÓN
-- =====================================================
-- Este script limpia cualquier transacción pendiente
-- y ejecuta la migración completa de hospitales
-- =====================================================

-- Terminar cualquier transacción pendiente
ROLLBACK;

-- Eliminar vistas existentes (si existen)
DROP VIEW IF EXISTS v_upcoming_appointments CASCADE;
DROP VIEW IF EXISTS v_room_usage_stats CASCADE;
DROP VIEW IF EXISTS v_consultation_rooms_with_specialties CASCADE;
DROP VIEW IF EXISTS v_specialties_with_rooms CASCADE;
DROP VIEW IF EXISTS v_hospitals_with_stats CASCADE;

-- Ahora ejecutar la migración completa
\i migration_add_hospitals.sql

