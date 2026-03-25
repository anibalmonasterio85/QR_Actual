"""
QR Access Control PRO - API Routes
JSON endpoints for frontend charts and external integrations.
"""
from flask import Blueprint, jsonify, request
from web_panel.utils.decorators import login_required
from web_panel.models import access_log, user as user_model

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/stats')
@login_required
def stats():
    """Get dashboard statistics."""
    stats_today = access_log.get_stats_today()
    stats_week = access_log.get_stats_week()
    total_users = user_model.count_users()
    active_users = user_model.count_active_users()
    hourly = access_log.get_stats_by_hour_today()

    return jsonify({
        'today': stats_today,
        'week': stats_week,
        'hourly': hourly,
        'users': {
            'total': total_users,
            'active': active_users
        }
    })


@api_bp.route('/accesos')
@login_required
def accesos():
    """Get recent access logs."""
    limit = request.args.get('limit', 20, type=int)
    logs = access_log.get_recent(limit=limit)

    result = []
    for log in logs:
        fecha = log.get('fecha_hora', '')
        if hasattr(fecha, 'isoformat'):
            fecha = fecha.isoformat()
        result.append({
            'id': log['id'],
            'nombre': log.get('nombre', 'Desconocido') or 'Desconocido',
            'resultado': log['resultado'],
            'fecha_hora': str(fecha),
            'scanner_id': log.get('scanner_id', 'main')
        })

    return jsonify({'accesos': result})


@api_bp.route('/validate_qr', methods=['POST'])
def validate_qr():
    """Validate a QR code (for external scanners via API)."""
    data = request.get_json()
    if not data or 'qr_code' not in data:
        return jsonify({'error': 'qr_code is required'}), 400

    qr_code = data['qr_code']
    user = user_model.get_by_qr(qr_code)

    if user and user['activo']:
        # Check expiration
        from datetime import datetime
        if user.get('fecha_expiracion') and user['fecha_expiracion'] < datetime.now():
            access_log.create_log(qr_code, 'denegado', user['id'],
                                  metodo='api', ip_address=request.remote_addr,
                                  detalles='QR expirado')
            return jsonify({'resultado': 'denegado', 'motivo': 'QR expirado', 'usuario': user['nombre']})

        access_log.create_log(qr_code, 'permitido', user['id'],
                              metodo='api', ip_address=request.remote_addr)
        return jsonify({
            'resultado': 'permitido',
            'usuario': user['nombre'],
            'rol': user['rol'],
            'departamento': user.get('departamento', '')
        })
    elif user and not user['activo']:
        access_log.create_log(qr_code, 'denegado', user['id'],
                              metodo='api', ip_address=request.remote_addr,
                              detalles='Usuario desactivado')
        return jsonify({'resultado': 'denegado', 'motivo': 'Usuario desactivado', 'usuario': user['nombre']})
    else:
        access_log.create_log(qr_code, 'denegado', metodo='api',
                              ip_address=request.remote_addr,
                              detalles='QR no registrado')
        return jsonify({'resultado': 'denegado', 'motivo': 'QR no registrado'})
@api_bp.route('/accesos/live')
@login_required
def accesos_live():
    """Get recent access logs for live updates."""
    logs = access_log.get_recent(limit=10)
    result = []
    for log in logs:
        fecha = log.get('fecha_hora', '')
        if hasattr(fecha, 'isoformat'):
            fecha = fecha.isoformat()
        result.append({
            'detalle': log.get('nombre') or log.get('qr_texto') or 'Desconocido',
            'resultado': log['resultado'].upper(),
            'fecha_hora': str(fecha)
        })
    return jsonify(result)


@api_bp.route('/accesos/filter', methods=['POST'])
@login_required
def filter_accesos():
    """Filter access logs via POST JSON."""
    data = request.get_json() or {}
    
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    resultado = data.get('resultado')
    busqueda = data.get('busqueda')
    
    logs = access_log.get_all_filtered(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        resultado=resultado,
        busqueda=busqueda,
        limit=50
    )
    
    result = []
    for log in logs:
        fecha = log.get('fecha_hora', '')
        if hasattr(fecha, 'isoformat'):
            fecha = fecha.isoformat()
        result.append({
            'detalle': log.get('nombre') or log.get('qr_texto') or 'Desconocido',
            'resultado': log['resultado'].upper(),
            'fecha_hora': str(fecha)
        })
    return jsonify(result)
