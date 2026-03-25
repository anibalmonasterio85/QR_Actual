"""
QR Access Control PRO - Scanner Routes
Web-based terminal for QR code scanning and validation.
"""
from flask import Blueprint, render_template, request, jsonify
from web_panel.utils.decorators import role_required, require_api_key
from web_panel.models import user as user_model, access_log
from datetime import datetime

scanner_bp = Blueprint('scanner', __name__, url_prefix='/scanner')


@scanner_bp.route('/')
@role_required('admin', 'guardia')
def scanner_view():
    """Render the web scanner terminal."""
    return render_template('scanner.html')


@scanner_bp.route('/validate', methods=['POST'])
@require_api_key
def validate_qr():
    """Validate a QR code and record the access attempt."""
    data = request.get_json()
    if not data or 'qr_code' not in data:
        return jsonify({"status": "error", "message": "No se recibió código QR"}), 400
        
    qr_code = data['qr_code']
    user = user_model.get_by_qr(qr_code)
    
    status = "error"
    mensaje = "Acceso Denegado"
    resultado_log = "denegado"
    detalles = ""

    if not user:
        mensaje = "Código no registrado en el sistema."
        detalles = "QR no registrado"
    elif not user['activo']:
        mensaje = "Usuario desactivado."
        detalles = "Usuario inactivo"
    elif user.get('fecha_expiracion') and user['fecha_expiracion'] < datetime.now():
        mensaje = "Código QR ha expirado."
        detalles = "QR expirado"
    else:
        status = "success"
        mensaje = f"Acceso concedido para {user['nombre']}"
        resultado_log = "permitido"
    
    # Record access in DB
    access_log.create_log(
        qr_texto=qr_code,
        resultado=resultado_log,
        user_id=user['id'] if user else None
    )
    
    return jsonify({
        "status": status,
        "message": mensaje,
        "user_name": user['nombre'] if user else "Desconocido",
        "company": user.get('departamento', 'General') if user else ""
    })
