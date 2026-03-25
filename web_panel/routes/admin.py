"""
QR Access Control PRO - Admin Routes
User management: CRUD, QR regeneration, reports export.
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
from web_panel.utils.decorators import admin_required
from web_panel.models import user as user_model, access_log
from web_panel.services import qr_service, export_service, email_service
from web_panel.app import mail
import io
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/usuarios')
@admin_required
def usuarios():
    """List all users with optional search/filter."""
    search = request.args.get('search', '')
    rol = request.args.get('rol', '')
    activo_filter = request.args.get('activo', '')

    activo = None
    if activo_filter == '1':
        activo = True
    elif activo_filter == '0':
        activo = False

    users = user_model.get_all(search=search or None, rol=rol or None, activo=activo)
    return render_template('admin_usuarios.html', usuarios=users, search=search, rol_filter=rol, activo_filter=activo_filter)


@admin_bp.route('/usuarios/crear', methods=['POST'])
@admin_required
def crear_usuario():
    """Create a new user."""
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    password = request.form.get('password', '').strip()
    rol = request.form.get('rol', 'usuario')
    departamento = request.form.get('departamento', '').strip()
    telefono = request.form.get('telefono', '').strip()

    if not nombre or not correo or not password:
        flash('Nombre, correo y contraseña son obligatorios.', 'warning')
        return redirect(url_for('admin.usuarios'))

    # Check if email already exists
    existing = user_model.get_by_email(correo)
    if existing:
        flash('Ya existe un usuario con ese correo.', 'danger')
        return redirect(url_for('admin.usuarios'))

    try:
        user_id = user_model.create_user(nombre, correo, password, rol, departamento or None, telefono or None)
        user = user_model.get_by_id(user_id)

        if user and user.get('qr_code'):
            qr_filename = qr_service.generate_qr_image(user['qr_code'])
            logger.info(f"QR generated for user {user_id}: {qr_filename}")

        flash(f'Usuario "{nombre}" creado exitosamente.', 'success')
        logger.info(f"User created: {correo} (ID: {user_id})")
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        flash(f'Error al crear usuario: {str(e)}', 'danger')

    return redirect(url_for('admin.usuarios'))


@admin_bp.route('/usuarios/<int:user_id>/editar', methods=['POST'])
@admin_required
def editar_usuario(user_id):
    """Edit user details."""
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    rol = request.form.get('rol', '')
    departamento = request.form.get('departamento', '').strip()
    telefono = request.form.get('telefono', '').strip()

    try:
        user_model.update_user(user_id,
                               nombre=nombre or None,
                               correo=correo or None,
                               rol=rol or None,
                               departamento=departamento or None,
                               telefono=telefono or None)
        flash('Usuario actualizado exitosamente.', 'success')
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        flash(f'Error al actualizar: {str(e)}', 'danger')

    return redirect(url_for('admin.usuarios'))


@admin_bp.route('/usuarios/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_usuario(user_id):
    """Toggle user active/inactive (POST only — prevents accidental GET triggering)."""
    try:
        user_model.toggle_active(user_id)
        user = user_model.get_by_id(user_id)
        estado = "activado" if user['activo'] else "desactivado"
        emoji = '✅' if user['activo'] else '🚫'
        flash(f'{emoji} Usuario "{user["nombre"]}" {estado} exitosamente.', 'success')
        logger.info(f"Admin toggled user {user_id}: {estado}")
    except Exception as e:
        logger.error(f"Toggle user {user_id} error: {e}")
        flash(f'Error al cambiar estado: {str(e)}', 'danger')
    return redirect(url_for('admin.usuarios'))


@admin_bp.route('/usuarios/<int:user_id>/regenerar-qr', methods=['POST'])
@admin_required
def regenerar_qr(user_id):
    """Regenerate QR code for a user and optionally email it (POST only)."""
    try:
        new_qr = user_model.regenerate_qr(user_id)
        qr_filename = qr_service.generate_qr_image(new_qr)
        qr_path = qr_service.get_qr_path(qr_filename)
        user = user_model.get_by_id(user_id)

        # Send new QR by email (non-blocking — failure does not abort the action)
        enviado = False
        if user and user.get('correo') and qr_path:
            try:
                enviado = email_service.send_qr_email(
                    mail, user['correo'], user['nombre'], qr_path
                )
            except Exception as mail_err:
                logger.warning(f"Admin QR regen: could not email user {user_id}: {mail_err}")

        msg = f'🔄 QR regenerado para "{user["nombre"]}"'
        msg += ' y enviado por correo.' if enviado else '. (No se pudo enviar correo)'
        flash(msg, 'success' if enviado else 'warning')
        logger.info(f"Admin regenerated QR for user {user_id}, email_sent={enviado}")
    except Exception as e:
        logger.error(f"Regenerar QR {user_id} error: {e}")
        flash(f'Error al regenerar QR: {str(e)}', 'danger')
    return redirect(url_for('admin.usuarios'))


@admin_bp.route('/usuarios/<int:user_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_usuario(user_id):
    """Delete a user (POST only — requires confirmation form submission)."""
    try:
        user = user_model.get_by_id(user_id)
        if not user:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('admin.usuarios'))
        if user['rol'] == 'admin' and user['id'] == session.get('user_id'):
            flash('⚠️ No puedes eliminar tu propia cuenta de administrador.', 'warning')
            return redirect(url_for('admin.usuarios'))
        nombre = user['nombre']
        user_model.delete_user(user_id)
        flash(f'🗑️ Usuario "{nombre}" eliminado exitosamente.', 'success')
        logger.info(f"Admin deleted user {user_id} ({nombre})")
    except Exception as e:
        logger.error(f"Delete user {user_id} error: {e}")
        flash(f'Error al eliminar: {str(e)}', 'danger')
    return redirect(url_for('admin.usuarios'))


@admin_bp.route('/usuarios/<int:user_id>/qr')
@admin_required
def ver_qr(user_id):
    """View/download a user's QR code image."""
    user = user_model.get_by_id(user_id)
    if not user or not user.get('qr_code'):
        flash('QR no encontrado.', 'danger')
        return redirect(url_for('admin.usuarios'))

    qr_filename = f"qr_{user['qr_code'][:16]}.png"
    qr_path = qr_service.get_qr_path(qr_filename)

    if not os.path.exists(qr_path):
        qr_filename = qr_service.generate_qr_image(user['qr_code'])
        qr_path = qr_service.get_qr_path(qr_filename)

    return send_file(qr_path, mimetype='image/png', as_attachment=False, download_name=f'qr_{user["nombre"]}.png')


@admin_bp.route('/reportes/accesos')
@admin_required
def reporte_accesos():
    """Export access logs report."""
    formato = request.args.get('formato', 'pdf')
    limit = int(request.args.get('limit', 200))

    logs = access_log.get_all_filtered(limit=limit)

    if formato == 'excel':
        data = export_service.export_excel(logs)
        return send_file(io.BytesIO(data), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name='reporte_accesos.xlsx')
    elif formato == 'word':
        data = export_service.export_word(logs)
        return send_file(io.BytesIO(data), mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         as_attachment=True, download_name='reporte_accesos.docx')
    else:
        data = export_service.export_pdf(logs)
        return send_file(io.BytesIO(data), mimetype='application/pdf',
                         as_attachment=True, download_name='reporte_accesos.pdf')
