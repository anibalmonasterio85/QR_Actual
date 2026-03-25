"""
Audit Service for QR Access PRO
Tracks all administrative actions for compliance and security.
"""
from config.database import execute_query
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def log_admin_action(admin_id, action, tabla, registro_id, cambios=None, ip_address=None):
    """
    Log an administrative action.
    
    Args:
        admin_id: ID of the admin performing the action
        action: Type of action (create, update, delete, toggle, export)
        tabla: Table affected (usuarios, accesos_log, etc)
        registro_id: ID of the affected record
        cambios: Dict of before/after values (optional)
        ip_address: IP address of requester (optional)
    
    Returns:
        True if logged, False otherwise
    """
    try:
        query = """
            INSERT INTO admin_logs 
            (admin_id, accion, tabla, registro_id, cambios, ip_address, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        import json
        cambios_json = json.dumps(cambios) if cambios else None
        
        execute_query(
            query,
            (admin_id, action, tabla, registro_id, cambios_json, ip_address, datetime.now()),
            commit=True
        )
        
        logger.info(f"Admin action logged: {action} on {tabla} by admin {admin_id}")
        return True
    except Exception as e:
        logger.error(f"Error logging admin action: {e}")
        return False


def get_admin_logs(admin_id=None, action=None, tabla=None, limit=100):
    """
    Get admin logs with optional filters.
    
    Args:
        admin_id: Filter by specific admin (optional)
        action: Filter by action type (optional)
        tabla: Filter by table (optional)
        limit: Number of records to return
    
    Returns:
        List of log records
    """
    query = "SELECT * FROM admin_logs WHERE 1=1"
    params = []
    
    if admin_id:
        query += " AND admin_id = %s"
        params.append(admin_id)
    if action:
        query += " AND accion = %s"
        params.append(action)
    if tabla:
        query += " AND tabla = %s"
        params.append(tabla)
    
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    
    return execute_query(query, tuple(params) if params else None, fetch_all=True) or []


def get_audit_report(start_date, end_date):
    """Get audit report for compliance."""
    query = """
        SELECT 
            admin_id, 
            accion, 
            tabla, 
            COUNT(*) as total_acciones,
            MIN(timestamp) as primer_accion,
            MAX(timestamp) as ultimo_accion
        FROM admin_logs
        WHERE timestamp BETWEEN %s AND %s
        GROUP BY admin_id, accion, tabla
        ORDER BY timestamp DESC
    """
    return execute_query(
        query,
        (start_date, end_date),
        fetch_all=True
    ) or []


def export_audit_logs(start_date, end_date, format='csv'):
    """
    Export audit logs for external analysis.
    
    Args:
        start_date: Start date for export
        end_date: End date for export
        format: 'csv' or 'json'
    
    Returns:
        Formatted audit data
    """
    logs = execute_query(
        "SELECT * FROM admin_logs WHERE timestamp BETWEEN %s AND %s ORDER BY timestamp DESC",
        (start_date, end_date),
        fetch_all=True
    ) or []
    
    if format == 'json':
        import json
        return json.dumps(logs, default=str, indent=2)
    
    # CSV format
    if not logs:
        return ""
    
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=logs[0].keys())
    writer.writeheader()
    writer.writerows(logs)
    
    return output.getvalue()
