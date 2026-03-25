"""
QR Access Control PRO - Route Decorators
Authentication and authorization decorators for Flask routes.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify


def login_required(f):
    """Decorator: require user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator: require user to be admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_rol') != 'admin':
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator: require user to have one of the specified roles.

    Usage:
        @role_required('admin', 'guardia')
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            if session.get('user_rol') not in roles:
                flash('No tienes permisos para acceder a esta sección.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
def require_api_key(f):
    """
    Decorator: require X-API-Key header.
    Matches the logic from the source project for inter-module communication.
    """
    import os
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        # Default key if not set in environment
        expected_key = os.environ.get('SCANNER_API_KEY', 'default-scanner-secret-key-2026')
        
        if not api_key or api_key != expected_key:
            return jsonify({
                "status": "error", 
                "message": "Acceso Denegado. API Key Inválida o faltante."
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function


def ajax_required(f):
    """Decorator: require the request to be an AJAX request."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return jsonify({"error": "AJAX request required"}), 403
        return f(*args, **kwargs)
    return decorated_function
