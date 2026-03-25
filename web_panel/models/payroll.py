"""
QR Access Control PRO - Shifts and Payroll Model
Manages work shifts, attendance tracking, and payroll calculations.
"""
from config.database import execute_query
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def create_shift(usuario_id, fecha, hora_entrada_esperada=None, hora_salida_esperada=None):
    """Create a new shift for a user."""
    query = """
        INSERT INTO turnos 
        (usuario_id, fecha, hora_entrada_esperada, hora_salida_esperada)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(
        query,
        (usuario_id, fecha, hora_entrada_esperada, hora_salida_esperada),
        commit=True
    )


def get_shifts_by_user(usuario_id, start_date=None, end_date=None):
    """Get shifts for a user."""
    query = "SELECT * FROM turnos WHERE usuario_id = %s"
    params = [usuario_id]
    
    if start_date:
        query += " AND fecha >= %s"
        params.append(start_date)
    if end_date:
        query += " AND fecha <= %s"
        params.append(end_date)
    
    query += " ORDER BY fecha DESC"
    return execute_query(query, tuple(params), fetch_all=True) or []


def create_jornada(usuario_id, fecha, acceso_entrada_id=None, acceso_salida_id=None):
    """Create a day record (jornada) - pairs entry and exit."""
    query = """
        INSERT INTO jornadas 
        (usuario_id, fecha, acceso_entrada_id, acceso_salida_id, estado)
        VALUES (%s, %s, %s, %s, 'incompleta')
    """
    return execute_query(
        query,
        (usuario_id, fecha, acceso_entrada_id, acceso_salida_id),
        commit=True
    )


def update_jornada_exit(jornada_id, acceso_salida_id):
    """Update jornada with exit access."""
    query = """
        UPDATE jornadas 
        SET acceso_salida_id = %s, estado = 'completa'
        WHERE id = %s
    """
    execute_query(query, (acceso_salida_id, jornada_id), commit=True)
    return calculate_jornada_hours(jornada_id)


def get_jornada_by_user_date(usuario_id, fecha):
    """Get jornada for user on specific date."""
    query = "SELECT * FROM jornadas WHERE usuario_id = %s AND fecha = %s"
    return execute_query(query, (usuario_id, fecha), fetch_one=True)


def calculate_jornada_hours(jornada_id):
    """Calculate working hours and delays for a jornada."""
    jornada = execute_query(
        "SELECT * FROM jornadas WHERE id = %s",
        (jornada_id,),
        fetch_one=True
    )
    
    if not jornada or not jornada.get('acceso_entrada_id') or not jornada.get('acceso_salida_id'):
        return False
    
    # Get access log entries
    entrada = execute_query(
        "SELECT fecha_hora FROM accesos_log WHERE id = %s",
        (jornada['acceso_entrada_id'],),
        fetch_one=True
    )
    salida = execute_query(
        "SELECT fecha_hora FROM accesos_log WHERE id = %s",
        (jornada['acceso_salida_id'],),
        fetch_one=True
    )
    
    if not entrada or not salida:
        return False
    
    # Calculate hours
    entrada_dt = entrada['fecha_hora']
    salida_dt = salida['fecha_hora']
    
    if isinstance(entrada_dt, str):
        entrada_dt = datetime.fromisoformat(entrada_dt)
    if isinstance(salida_dt, str):
        salida_dt = datetime.fromisoformat(salida_dt)
    
    delta = salida_dt - entrada_dt
    horas_trabajadas = delta.total_seconds() / 3600
    
    # Get expected hours from shift
    turno = execute_query(
        "SELECT * FROM turnos WHERE usuario_id = %s AND fecha = %s",
        (jornada['usuario_id'], jornada['fecha']),
        fetch_one=True
    )
    
    atrasos_minutos = 0
    if turno and turno.get('hora_entrada_esperada'):
        esperada_dt = datetime.combine(
            jornada['fecha'],
            turno['hora_entrada_esperada']
        )
        if entrada_dt > esperada_dt:
            atrasos_minutos = int((entrada_dt - esperada_dt).total_seconds() / 60)
    
    # Update jornada with calculations
    query = """
        UPDATE jornadas 
        SET 
            hora_entrada_real = %s,
            hora_salida_real = %s,
            horas_trabajadas = %s,
            atrasos_minutos = %s
        WHERE id = %s
    """
    execute_query(
        query,
        (
            entrada_dt.time(),
            salida_dt.time(),
            round(horas_trabajadas, 2),
            atrasos_minutos,
            jornada_id
        ),
        commit=True
    )
    
    logger.info(f"Jornada {jornada_id} calculated: {horas_trabajadas:.2f}h, {atrasos_minutos}min delay")
    return True


def get_payroll_report(usuario_id, start_date, end_date):
    """Get payroll report for a user."""
    query = """
        SELECT 
            fecha,
            horas_trabajadas,
            atrasos_minutos,
            estado,
            acceso_entrada_id is not null as entrada_registrada,
            acceso_salida_id is not null as salida_registrada
        FROM jornadas
        WHERE usuario_id = %s AND fecha BETWEEN %s AND %s
        ORDER BY fecha DESC
    """
    
    jornadas = execute_query(
        query,
        (usuario_id, start_date, end_date),
        fetch_all=True
    ) or []
    
    if not jornadas:
        return {
            "usuario_id": usuario_id,
            "periodo": f"{start_date} a {end_date}",
            "total_horas": 0,
            "total_atrasos_minutos": 0,
            "jornadas": []
        }
    
    total_horas = sum(j.get('horas_trabajadas', 0) or 0 for j in jornadas)
    total_atrasos = sum(j.get('atrasos_minutos', 0) or 0 for j in jornadas)
    
    return {
        "usuario_id": usuario_id,
        "periodo": f"{start_date} a {end_date}",
        "total_dias": len(jornadas),
        "total_horas": round(total_horas, 2),
        "total_atrasos_minutos": total_atrasos,
        "atrasos_promedio_minutos": round(total_atrasos / len(jornadas), 1) if jornadas else 0,
        "jornadas": jornadas
    }


def export_payroll_csv(usuario_id, start_date, end_date):
    """Export payroll data as CSV."""
    import csv
    from io import StringIO
    
    report = get_payroll_report(usuario_id, start_date, end_date)
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["QR Access PRO - Reporte de Nómina"])
    writer.writerow(["Usuario ID", usuario_id])
    writer.writerow(["Período", report["periodo"]])
    writer.writerow([])
    writer.writerow(["Fecha", "Horas Trabajadas", "Atrasos (min)", "Estado"])
    
    for jornada in report["jornadas"]:
        writer.writerow([
            jornada["fecha"],
            jornada["horas_trabajadas"],
            jornada["atrasos_minutos"],
            jornada["estado"]
        ])
    
    writer.writerow([])
    writer.writerow(["Total Horas", report["total_horas"]])
    writer.writerow(["Total Atrasos (minutos)", report["total_atrasos_minutos"]])
    
    return output.getvalue()
