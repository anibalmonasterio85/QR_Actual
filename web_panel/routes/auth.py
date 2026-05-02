"""
QR Access Control PRO - Auth Routes
Login, logout, and public registration with email notifications.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from web_panel.models import user as user_model
from web_panel.services import qr_service, email_service
from web_panel.app import limiter
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute", error_message="Demasiados intentos. Por favor espera 1 minuto.")
def login():
    """Login page and authentication."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '').strip()

        if not correo or not password:
            flash('Por favor, completa todos los campos.', 'warning')
            return render_template('login.html')

        user = user_model.authenticate(correo, password)
        if user:
            session['user_id'] = user['id']
            session['user_nombre'] = user['nombre']
            session['user_correo'] = user['correo']
            session['user_rol'] = user['rol']
            session.permanent = True
            logger.info(f"Login exitoso: {correo}")
            flash(f'Bienvenido, {user["nombre"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            logger.warning(f"Login fallido: {correo}")
            flash('Credenciales incorrectas o cuenta desactivada.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute", error_message="Demasiados intentos de registro. Por favor espera 1 minuto.")
def register():
    """Public registration page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        departamento = request.form.get('departamento', '').strip()
        telefono = request.form.get('telefono', '').strip()

        # Validations
        if not nombre or not correo or not password:
            flash('Nombre, correo y contraseña son obligatorios.', 'warning')
            return render_template('register.html')

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
            return render_template('register.html')

        if password != password2:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register.html')

        existing = user_model.get_by_email(correo)
        if existing:
            flash('Ya existe una cuenta con ese correo electrónico.', 'danger')
            return render_template('register.html')

        try:
            # Create user with 'usuario' role (never admin)
            user_id = user_model.create_user(
                nombre=nombre,
                correo=correo,
                password=password,
                rol='usuario',
                departamento=departamento or None,
                telefono=telefono or None
            )

            # Generate QR image
            user = user_model.get_by_id(user_id)
            qr_path = None
            if user and user.get('qr_code'):
                qr_filename = qr_service.generate_qr_image(user['qr_code'])
                qr_path = qr_service.get_qr_path(qr_filename)
                logger.info(f"QR generated for new user {correo}")

            # Send welcome email with QR
            if qr_path:
                try:
                    from web_panel.app import mail
                    email_service.send_qr_email(mail, correo, nombre, qr_path)
                    logger.info(f"Welcome email sent to {correo}")
                except Exception as mail_err:
                    logger.warning(f"Could not send welcome email: {mail_err}")

            logger.info(f"Registration successful: {correo} (ID: {user_id})")
            flash('¡Cuenta creada exitosamente! Tu código QR está listo. Inicia sesión para verlo.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            logger.error(f"Registration error: {e}")
            flash(f'Error al crear la cuenta: {str(e)}', 'danger')

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """Logout and clear session."""
    nombre = session.get('user_nombre', 'Usuario')
    session.clear()
    flash(f'Hasta luego, {nombre}!', 'info')
    return redirect(url_for('auth.login'))
