-- QR Access PRO - Schema Extensions
-- Extensions for enhanced functionality

-- 1. Email Confirmation Tokens
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_confirmado BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_token VARCHAR(255) UNIQUE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_token_expira DATETIME;

-- 2. TOTP Secret for Dynamic QR
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(255);

-- 3. Admin Audit Logs
CREATE TABLE IF NOT EXISTS admin_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    admin_id INT NOT NULL,
    accion VARCHAR(50) NOT NULL,
    tabla VARCHAR(50) NOT NULL,
    registro_id INT,
    cambios JSON,
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_admin_id (admin_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_accion (accion),
    FOREIGN KEY (admin_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Zonas de Acceso (Multi-Zone RBAC)
CREATE TABLE IF NOT EXISTS zonas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    ubicacion VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Permisos de Usuario por Zona
CREATE TABLE IF NOT EXISTS usuario_zona_permisos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    zona_id INT NOT NULL,
    permiso VARCHAR(50) DEFAULT 'lectura',
    asignado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_usuario_zona (usuario_id, zona_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (zona_id) REFERENCES zonas(id) ON DELETE CASCADE,
    INDEX idx_usuario_id (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Turnos y Control de Horario
CREATE TABLE IF NOT EXISTS turnos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada_esperada TIME,
    hora_salida_esperada TIME,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_usuario_fecha (usuario_id, fecha),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Jornadas (Empareamiento de entrada/salida)
CREATE TABLE IF NOT EXISTS jornadas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    fecha DATE NOT NULL,
    acceso_entrada_id BIGINT,
    acceso_salida_id BIGINT,
    hora_entrada_real TIME,
    hora_salida_real TIME,
    horas_trabajadas DECIMAL(5,2),
    atrasos_minutos INT DEFAULT 0,
    extras_minutos INT DEFAULT 0,
    estado VARCHAR(50) DEFAULT 'incompleta',
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (acceso_entrada_id) REFERENCES accesos_log(id),
    FOREIGN KEY (acceso_salida_id) REFERENCES accesos_log(id),
    INDEX idx_usuario_fecha (usuario_id, fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Tokens de Email para Recuperación de Contraseña
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Índices Optimizados para Performance
ALTER TABLE accesos_log ADD INDEX IF NOT EXISTS idx_user_fecha (user_id, fecha_hora DESC);
ALTER TABLE accesos_log ADD INDEX IF NOT EXISTS idx_resultado_fecha (resultado, fecha_hora DESC);
ALTER TABLE usuarios ADD INDEX IF NOT EXISTS idx_email_activo (correo, activo);

-- 10. Geocoordenadas para accesos (Geolocalización)
ALTER TABLE accesos_log ADD COLUMN IF NOT EXISTS latitud DECIMAL(10, 8);
ALTER TABLE accesos_log ADD COLUMN IF NOT EXISTS longitud DECIMAL(11, 8);
ALTER TABLE accesos_log ADD COLUMN IF NOT EXISTS ciudad VARCHAR(100);
ALTER TABLE accesos_log ADD COLUMN IF NOT EXISTS pais VARCHAR(100);
