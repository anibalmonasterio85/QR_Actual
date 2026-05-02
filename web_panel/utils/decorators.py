"""
QR Access Control PRO - Route Decorators
Authentication and authorization decorators for Flask routes.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request


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
