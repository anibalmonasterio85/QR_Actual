"""
QR Access Control PRO - Dashboard Routes
Main panel with statistics, charts, and Mi QR page.
"""
import os
from flask import Blueprint, render_template, session, redirect, url_for, flash
from web_panel.utils.decorators import login_required
from web_panel.models import access_log, user as user_model
from web_panel.services import qr_service, email_service
import logging

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard with stats and charts.

    Redirects 'usuario' role to /mi-qr — the stats dashboard is for admin/guardia only.
    """
    # Regular users have no business on the stats dashboard
    if session.get('user_rol') == 'usuario':
        return redirect(url_for('dashboard.mi_qr'))

    stats_today = access_log.get_stats_today()
    stats_week = access_log.get_stats_week()
    recent_logs = access_log.get_recent(limit=10)
    total_users = user_model.count_users()
    active_users = user_model.count_active_users()

    return render_template('panel.html',
                           stats_today=stats_today,
                           stats_week=stats_week,
                           recent_logs=recent_logs,
                           total_users=total_users,
                           active_users=active_users)


@dashboard_bp.route('/mi-qr')
@login_required
def mi_qr():
    """Show the authenticated user's QR code."""
    user_id = session.get('user_id')
    user = user_model.get_by_id(user_id)

    qr_image_url = None
    if user and user.get('qr_code'):
        qr_filename = f"qr_{user['qr_code'][:16]}.png"
        qr_path = qr_service.get_qr_path(qr_filename)

        # Generate if doesn't exist
        if not os.path.exists(qr_path):
            qr_filename = qr_service.generate_qr_image(user['qr_code'])

        qr_image_url = url_for('static', filename=f'qrcodes/{qr_filename}')

    # Get user's own access logs
    my_logs = access_log.get_all_filtered(user_id=user_id, limit=10)

    return render_template('mi_qr.html',
                           qr_image_url=qr_image_url,
                           my_logs=my_logs)


@dashboard_bp.route('/mi-qr/regenerar')
@login_required
def regenerar_mi_qr():
    """Regenerate the authenticated user's QR code and send by email.
    Enforces a 5-minute cooldown between regenerations to prevent email spam.
    """
    from datetime import datetime, timezone

    user_id = session.get('user_id')

    # ── Cooldown check (5 minutes) ──────────────────────────────────────────
    COOLDOWN_SECONDS = 300  # 5 minutes
    last_regen = session.get('last_qr_regen')

    if last_regen:
        elapsed = (datetime.now(timezone.utc).timestamp()) - last_regen
        if elapsed < COOLDOWN_SECONDS:
            remaining = int((COOLDOWN_SECONDS - elapsed) / 60) + 1
            flash(
                f'⏳ Puedes regenerar tu QR nuevamente en {remaining} minuto(s). '
                f'Espera antes de volver a intentarlo.',
                'warning'
            )
            logger.info(f"QR regen cooldown for user {user_id}: {elapsed:.0f}s elapsed")
            return redirect(url_for('dashboard.mi_qr'))
    # ────────────────────────────────────────────────────────────────────────

    try:
        new_qr = user_model.regenerate_qr(user_id)
        qr_filename = qr_service.generate_qr_image(new_qr)
        qr_path = qr_service.get_qr_path(qr_filename)

        # Record successful regeneration timestamp in session
        session['last_qr_regen'] = datetime.now(timezone.utc).timestamp()

        # Send new QR by email
        user = user_model.get_by_id(user_id)
        if user and qr_path:
            try:
                from web_panel.app import mail
                sent = email_service.send_qr_email(mail, user['correo'], user['nombre'], qr_path)
                if sent:
                    flash('✅ Tu código QR ha sido regenerado y enviado a tu correo.', 'success')
                else:
                    flash('✅ QR regenerado. No se pudo enviar el correo (revisa la configuración SMTP).', 'warning')
                logger.info(f"QR email sent={sent} for user {user_id}")
            except Exception as mail_err:
                logger.warning(f"Could not send QR email: {mail_err}")
                flash('✅ QR regenerado exitosamente. Error al enviar correo.', 'warning')
        else:
            flash('✅ Tu código QR ha sido regenerado exitosamente.', 'success')

        logger.info(f"User {user_id} regenerated their QR code")

    except Exception as e:
        logger.error(f"QR regeneration error for user {user_id}: {e}")
        flash(f'❌ Error al regenerar el QR: {str(e)}', 'danger')

    return redirect(url_for('dashboard.mi_qr'))
