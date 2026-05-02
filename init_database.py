"""
QR Access Control PRO - Database Initialization Script
Creates database, tables, and default admin user.
"""
import mysql.connector
import sys

# Config - match your MySQL setup
DB_HOST = '127.0.0.1'
DB_PORT = 3307
DB_USER = 'root'
DB_PASSWORD = 'admin'
DB_NAME = 'qr_access'


def init_database():
    print("\n🔐 QR Access Control PRO - Database Setup\n")

    # Step 1: Connect without database to create it
    print("[1/3] Connecting to MySQL...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        print(f"  ✅ Connected to MySQL at {DB_HOST}:{DB_PORT}")
    except mysql.connector.Error as e:
        print(f"  ❌ Cannot connect to MySQL: {e}")
        print(f"  Check: host={DB_HOST}, port={DB_PORT}, user={DB_USER}")
        sys.exit(1)

    # Step 2: Create database and tables
    print("[2/3] Creating database and tables...")
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{DB_NAME}`")

        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ Table 'usuarios' created")

        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ Table 'accesos_log' created")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                id INT AUTO_INCREMENT PRIMARY KEY,
                clave VARCHAR(100) NOT NULL UNIQUE,
                valor TEXT NOT NULL,
                descripcion VARCHAR(255) NULL,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("  ✅ Table 'configuracion' created")

        # Default config
        config_values = [
            ('app_name', 'QR Access Control PRO', 'Nombre de la aplicacion'),
            ('session_timeout', '3600', 'Timeout de sesion en segundos'),
            ('max_login_attempts', '5', 'Intentos maximos de login'),
            ('qr_expiration_days', '365', 'Dias de expiracion de QR'),
            ('timezone', 'America/Argentina/Buenos_Aires', 'Zona horaria'),
        ]
        for clave, valor, desc in config_values:
            cursor.execute(
                "INSERT IGNORE INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)",
                (clave, valor, desc)
            )

        conn.commit()
        print("  ✅ Default configuration inserted")

    except mysql.connector.Error as e:
        print(f"  ❌ Error creating tables: {e}")
        conn.rollback()
        sys.exit(1)

    # Step 3: Verify
    print("[3/3] Verifying tables...")
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"  ✅ Tables: {', '.join(tables)}")

    cursor.close()
    conn.close()

    print(f"\n{'='*50}")
    print(f"  ✅ DATABASE '{DB_NAME}' READY!")
    print(f"  Now run: python web_panel/app.py")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    init_database()
