-- ============================================
-- QR Access Control PRO - Database Schema
-- MySQL 8.x | Port 3307 | User: admin
-- ============================================

CREATE DATABASE IF NOT EXISTS qr_access
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE qr_access;

-- ============================================
-- Table: usuarios
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'usuario', 'visitante') NOT NULL DEFAULT 'usuario',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_expiracion DATETIME NULL,
    qr_code VARCHAR(255) UNIQUE,
    foto VARCHAR(255) NULL,
    departamento VARCHAR(100) NULL,
    telefono VARCHAR(20) NULL,
    notas TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_correo (correo),
    INDEX idx_qr_code (qr_code),
    INDEX idx_rol (rol),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: accesos_log
-- ============================================
CREATE TABLE IF NOT EXISTS accesos_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    qr_texto VARCHAR(255) NOT NULL,
    resultado ENUM('permitido', 'denegado') NOT NULL,
    user_id INT NULL,
    metodo VARCHAR(50) DEFAULT 'qr_scanner',
    ip_address VARCHAR(45) NULL,
    scanner_id VARCHAR(50) DEFAULT 'main',
    detalles TEXT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_resultado (resultado),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: configuracion
-- ============================================
CREATE TABLE IF NOT EXISTS configuracion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion VARCHAR(255) NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Default configuration
-- ============================================
INSERT IGNORE INTO configuracion (clave, valor, descripcion) VALUES
('app_name', 'QR Access Control PRO', 'Nombre de la aplicación'),
('session_timeout', '3600', 'Timeout de sesión en segundos'),
('max_login_attempts', '5', 'Intentos máximos de login'),
('qr_expiration_days', '365', 'Días de expiración de QR por defecto'),
('timezone', 'America/Argentina/Buenos_Aires', 'Zona horaria del sistema');

-- ============================================
-- Default admin user (password: admin123)
-- Hash generated with: hashlib.sha256
-- IMPORTANT: Change this password immediately!
-- ============================================
-- The admin user will be inserted by the app initialization script
