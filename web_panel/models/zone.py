"""
QR Access Control PRO - Multi-Zone RBAC Model
Manages zones/areas and user permissions for physical access control.
"""
from config.database import execute_query
import logging

logger = logging.getLogger(__name__)


def create_zone(nombre, descripcion=None, ubicacion=None):
    """Create a new access zone."""
    query = """
        INSERT INTO zonas (nombre, descripcion, ubicacion, activo)
        VALUES (%s, %s, %s, TRUE)
    """
    return execute_query(
        query,
        (nombre, descripcion, ubicacion),
        commit=True
    )


def get_zone(zona_id):
    """Get zone details."""
    query = "SELECT * FROM zonas WHERE id = %s"
    return execute_query(query, (zona_id,), fetch_one=True)


def get_all_zones():
    """Get all active zones."""
    query = "SELECT * FROM zonas WHERE activo = TRUE ORDER BY nombre"
    return execute_query(query, fetch_all=True) or []


def update_zone(zona_id, nombre=None, descripcion=None, ubicacion=None, activo=None):
    """Update zone details."""
    fields = []
    params = []
    
    if nombre is not None:
        fields.append("nombre = %s")
        params.append(nombre)
    if descripcion is not None:
        fields.append("descripcion = %s")
        params.append(descripcion)
    if ubicacion is not None:
        fields.append("ubicacion = %s")
        params.append(ubicacion)
    if activo is not None:
        fields.append("activo = %s")
        params.append(activo)
    
    if not fields:
        return False
    
    params.append(zona_id)
    query = f"UPDATE zonas SET {', '.join(fields)} WHERE id = %s"
    execute_query(query, tuple(params), commit=True)
    return True


def assign_user_to_zone(usuario_id, zona_id, permiso='lectura'):
    """Assign a user to a zone with specific permissions."""
    query = """
        INSERT INTO usuario_zona_permisos (usuario_id, zona_id, permiso)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE permiso = %s
    """
    execute_query(
        query,
        (usuario_id, zona_id, permiso, permiso),
        commit=True
    )
    logger.info(f"User {usuario_id} assigned to zone {zona_id} with {permiso} permission")
    return True


def remove_user_from_zone(usuario_id, zona_id):
    """Remove user from zone."""
    query = "DELETE FROM usuario_zona_permisos WHERE usuario_id = %s AND zona_id = %s"
    execute_query(query, (usuario_id, zona_id), commit=True)
    return True


def get_user_zones(usuario_id):
    """Get all zones a user has access to."""
    query = """
        SELECT z.id, z.nombre, z.descripcion, z.ubicacion, uzp.permiso
        FROM zonas z
        JOIN usuario_zona_permisos uzp ON z.id = uzp.zona_id
        WHERE uzp.usuario_id = %s AND z.activo = TRUE
    """
    return execute_query(query, (usuario_id,), fetch_all=True) or []


def get_zone_users(zona_id):
    """Get all users with access to a zone."""
    query = """
        SELECT u.id, u.nombre, u.correo, u.rol, uzp.permiso
        FROM usuarios u
        JOIN usuario_zona_permisos uzp ON u.id = uzp.usuario_id
        WHERE uzp.zona_id = %s AND u.activo = TRUE
    """
    return execute_query(query, (zona_id,), fetch_all=True) or []


def can_user_access_zone(usuario_id, zona_id):
    """Check if user has access to zone."""
    # Admin can access all zones
    user = execute_query("SELECT rol FROM usuarios WHERE id = %s", (usuario_id,), fetch_one=True)
    if user and user['rol'] == 'admin':
        return True
    
    # Check zone permission
    query = """
        SELECT COUNT(*) as count FROM usuario_zona_permisos
        WHERE usuario_id = %s AND zona_id = %s
    """
    result = execute_query(query, (usuario_id, zona_id), fetch_one=True)
    return result and result['count'] > 0


def log_zone_access(usuario_id, zona_id, resultado, metodo='qr', ip_address=None):
    """Log access attempt to a specific zone."""
    # Get access_log entry with zona info
    query = """
        INSERT INTO accesos_log 
        (user_id, qr_texto, resultado, metodo, ip_address, scanner_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    execute_query(
        query,
        (usuario_id, f"zona:{zona_id}", resultado, metodo, ip_address, f"zone_{zona_id}"),
        commit=True
    )
    
    logger.info(f"Zone access: user {usuario_id} to zone {zona_id}: {resultado}")
    return True


def get_zone_access_stats(zona_id, start_date=None, end_date=None):
    """Get access statistics for a zone."""
    query = "SELECT * FROM accesos_log WHERE scanner_id = %s"
    params = [f"zone_{zona_id}"]
    
    if start_date:
        query += " AND fecha_hora >= %s"
        params.append(start_date)
    if end_date:
        query += " AND fecha_hora <= %s"
        params.append(end_date)
    
    logs = execute_query(query, tuple(params), fetch_all=True) or []
    
    permitidos = sum(1 for log in logs if log['resultado'] == 'permitido')
    denegados = sum(1 for log in logs if log['resultado'] == 'denegado')
    
    return {
        "zona_id": zona_id,
        "total_accesos": len(logs),
        "permitidos": permitidos,
        "denegados": denegados,
        "tasa_exito": round(permitidos / len(logs) * 100, 2) if logs else 0,
        "logs": logs
    }


def bulk_assign_users_to_zone(user_ids, zona_id, permiso='lectura'):
    """Assign multiple users to a zone."""
    count = 0
    for user_id in user_ids:
        try:
            assign_user_to_zone(user_id, zona_id, permiso)
            count += 1
        except Exception as e:
            logger.error(f"Error assigning user {user_id} to zone {zona_id}: {e}")
    
    logger.info(f"Bulk assigned {count}/{len(user_ids)} users to zone {zona_id}")
    return count
