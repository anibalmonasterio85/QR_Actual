"""
QR Access Control PRO - User Model
CRUD operations for the usuarios table.
Uses werkzeug for secure password hashing (scrypt).

Actual DB columns: id, nombre, rut, correo, empresa_id, departamento,
                   telefono, notas, password_hash, rol, activo,
                   fecha_expiracion, qr_code, creado_en
"""
from config.database import execute_query
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import logging

logger = logging.getLogger(__name__)


def hash_password(password):
    """Hash a password using werkzeug (scrypt)."""
    return generate_password_hash(password)


def verify_password(password, password_hash):
    """Verify a password against its werkzeug hash."""
    try:
        return check_password_hash(password_hash, password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_user(nombre, correo, password, rol='usuario', departamento=None, telefono=None, notas=None):
    """Create a new user and return its ID."""
    qr_code = secrets.token_urlsafe(32)
    password_h = hash_password(password)
    query = """
        INSERT INTO usuarios (nombre, correo, password_hash, rol, qr_code, departamento, telefono, notas)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (nombre, correo, password_h, rol, qr_code, departamento, telefono, notas), commit=True)


def get_by_id(user_id):
    """Get user by ID."""
    return execute_query("SELECT * FROM usuarios WHERE id = %s", (user_id,), fetch_one=True)


def get_by_email(correo):
    """Get user by email."""
    return execute_query("SELECT * FROM usuarios WHERE correo = %s", (correo,), fetch_one=True)


def get_by_qr(qr_code):
    """Get user by QR code token."""
    return execute_query("SELECT * FROM usuarios WHERE qr_code = %s", (qr_code,), fetch_one=True)


def authenticate(correo, password):
    """Authenticate user with email and password. Returns user dict or None."""
    user = get_by_email(correo)
    if not user:
        logger.warning(f"Auth: user not found: {correo}")
        return None

    if not verify_password(password, user['password_hash']):
        logger.warning(f"Auth: bad password for: {correo}")
        return None

    if not user['activo']:
        logger.warning(f"Auth: inactive user: {correo}")
        return None

    logger.info(f"Auth: success for: {correo}")
    return user


def get_all(search=None, rol=None, activo=None):
    """Get all users with optional filters."""
    query = """SELECT id, nombre, correo, rol, activo, departamento, telefono,
                      qr_code, fecha_expiracion, creado_en
               FROM usuarios WHERE 1=1"""
    params = []

    if search:
        query += " AND (nombre LIKE %s OR correo LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    if rol:
        query += " AND rol = %s"
        params.append(rol)
    if activo is not None:
        query += " AND activo = %s"
        params.append(activo)

    query += " ORDER BY creado_en DESC"
    return execute_query(query, tuple(params) if params else None, fetch_all=True)


def update_user(user_id, nombre=None, correo=None, rol=None, departamento=None, telefono=None, notas=None, fecha_expiracion=None):
    """Update user fields."""
    fields = []
    params = []

    if nombre is not None:
        fields.append("nombre = %s")
        params.append(nombre)
    if correo is not None:
        fields.append("correo = %s")
        params.append(correo)
    if rol is not None:
        fields.append("rol = %s")
        params.append(rol)
    if departamento is not None:
        fields.append("departamento = %s")
        params.append(departamento)
    if telefono is not None:
        fields.append("telefono = %s")
        params.append(telefono)
    if notas is not None:
        fields.append("notas = %s")
        params.append(notas)
    if fecha_expiracion is not None:
        fields.append("fecha_expiracion = %s")
        params.append(fecha_expiracion)

    if not fields:
        return False

    params.append(user_id)
    query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"
    execute_query(query, tuple(params), commit=True)
    return True


def toggle_active(user_id):
    """Toggle user active status."""
    execute_query("UPDATE usuarios SET activo = NOT activo WHERE id = %s", (user_id,), commit=True)
    return True


def update_password(user_id, new_password):
    """Update user password."""
    password_h = hash_password(new_password)
    execute_query("UPDATE usuarios SET password_hash = %s WHERE id = %s", (password_h, user_id), commit=True)
    return True


def regenerate_qr(user_id):
    """Generate a new QR code for a user."""
    new_qr = secrets.token_urlsafe(32)
    execute_query("UPDATE usuarios SET qr_code = %s WHERE id = %s", (new_qr, user_id), commit=True)
    return new_qr


def delete_user(user_id):
    """Delete a user."""
    execute_query("DELETE FROM usuarios WHERE id = %s", (user_id,), commit=True)
    return True


def count_users():
    """Count total users."""
    result = execute_query("SELECT COUNT(*) as total FROM usuarios", fetch_one=True)
    return result['total'] if result else 0


def count_active_users():
    """Count active users."""
    result = execute_query("SELECT COUNT(*) as total FROM usuarios WHERE activo = TRUE", fetch_one=True)
    return result['total'] if result else 0
