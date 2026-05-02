-- ============================================================
-- QR Access Control PRO — Índices de Rendimiento
-- Ejecutar una sola vez contra la BD qr_access (puerto 3307)
-- ============================================================

USE qr_access;

-- Índice en fecha_hora para ORDER BY rápido en logs de acceso
CREATE INDEX IF NOT EXISTS idx_accesos_fecha
    ON accesos_log (fecha_hora DESC);

-- Índice en user_id para JOINs con usuarios y filtros por usuario
CREATE INDEX IF NOT EXISTS idx_accesos_user
    ON accesos_log (user_id);

-- Índice en resultado para estadísticas ('permitido' / 'denegado')
CREATE INDEX IF NOT EXISTS idx_accesos_resultado
    ON accesos_log (resultado);

-- Verificar índices creados
SHOW INDEX FROM accesos_log;
