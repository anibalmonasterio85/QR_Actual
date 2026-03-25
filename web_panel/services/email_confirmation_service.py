"""
Email Confirmation Service for QR Access PRO
Handles email verification, password reset tokens, and email notifications.
"""
from config.database import execute_query
from web_panel.services.email_service import send_email
import secrets
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def generate_email_token():
    """Generate a secure email confirmation token."""
    return secrets.token_urlsafe(32)


def create_email_confirmation_token(usuario_id):
    """Create an email confirmation token for a user."""
    token = generate_email_token()
    expira = datetime.now() + timedelta(days=1)  # 24 hours
    
    query = """
        UPDATE usuarios 
        SET email_token = %s, email_token_expira = %s, email_confirmado = FALSE
        WHERE id = %s
    """
    execute_query(query, (token, expira, usuario_id), commit=True)
    
    logger.info(f"Email confirmation token created for user {usuario_id}")
    return token


def verify_email_token(usuario_id, token):
    """Verify an email confirmation token."""
    query = """
        SELECT email_token, email_token_expira, email_confirmado
        FROM usuarios
        WHERE id = %s
    """
    user = execute_query(query, (usuario_id,), fetch_one=True)
    
    if not user:
        return False, "Usuario no encontrado"
    
    if user['email_confirmado']:
        return False, "Email ya confirmado"
    
    if not user['email_token']:
        return False, "No hay token pendiente"
    
    if user['email_token'] != token:
        return False, "Token inválido"
    
    if datetime.now() > user['email_token_expira']:
        return False, "Token expirado"
    
    # Mark email as confirmed
    query = """
        UPDATE usuarios 
        SET email_confirmado = TRUE, email_token = NULL, email_token_expira = NULL
        WHERE id = %s
    """
    execute_query(query, (usuario_id,), commit=True)
    
    logger.info(f"Email confirmed for user {usuario_id}")
    return True, "Email confirmado correctamente"


def send_email_confirmation(usuario_id, usuario_email, usuario_nombre):
    """Send email confirmation message."""
    token = create_email_confirmation_token(usuario_id)
    
    # Build confirmation link (adjust domain as needed)
    confirm_url = f"http://localhost:5000/auth/confirm-email?user={usuario_id}&token={token}"
    
    subject = "Confirma tu correo electrónico - QR Access PRO"
    html_body = f"""
    <html>
        <body style="font-family: 'Inter', sans-serif; background: #0a0a1a; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: rgba(25,25,60,0.7); 
                        padding: 30px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                <h2 style="color: #e8e8f0; margin-bottom: 20px;">¡Bienvenido a QR Access PRO!</h2>
                <p style="color: #a0a0c0; margin-bottom: 15px;">Hola <strong>{usuario_nombre}</strong>,</p>
                <p style="color: #a0a0c0; margin-bottom: 20px;">
                    Por favor confirma tu dirección de correo electrónico para completar tu registro.
                </p>
                <a href="{confirm_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none;
                   font-weight: 600; margin-bottom: 20px;">Confirmar Email</a>
                <p style="color: #6a6a8a; font-size: 12px; margin-bottom: 10px;">
                    O copia este link en tu navegador:
                </p>
                <p style="color: #6a6a8a; font-size: 11px; word-break: break-all; 
                          background: rgba(0,0,0,0.3); padding: 10px; border-radius: 4px;">
                    {confirm_url}
                </p>
                <p style="color: #6a6a8a; font-size: 12px; margin-top: 20px;">
                    Este link expira en 24 horas.
                </p>
                <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0;">
                <p style="color: #6a6a8a; font-size: 11px;">
                    © 2026 QR Access PRO. Sistema de Control de Acceso.
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(usuario_email, subject, html_body)


def create_password_reset_token(usuario_id):
    """Create a password reset token."""
    token = generate_email_token()
    expires_at = datetime.now() + timedelta(hours=2)
    
    query = """
        INSERT INTO password_reset_tokens (usuario_id, token, expires_at)
        VALUES (%s, %s, %s)
    """
    execute_query(query, (usuario_id, token, expires_at), commit=True)
    
    logger.info(f"Password reset token created for user {usuario_id}")
    return token


def verify_password_reset_token(token):
    """Verify a password reset token."""
    query = """
        SELECT usuario_id FROM password_reset_tokens
        WHERE token = %s AND used = FALSE AND expires_at > NOW()
    """
    result = execute_query(query, (token,), fetch_one=True)
    
    if not result:
        return None
    
    return result['usuario_id']


def use_password_reset_token(token):
    """Mark password reset token as used."""
    query = "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s"
    execute_query(query, (token,), commit=True)


def send_password_reset_email(usuario_id, usuario_email, usuario_nombre):
    """Send password reset email."""
    token = create_password_reset_token(usuario_id)
    
    reset_url = f"http://localhost:5000/auth/reset-password?token={token}"
    
    subject = "Recupera tu contraseña - QR Access PRO"
    html_body = f"""
    <html>
        <body style="font-family: 'Inter', sans-serif; background: #0a0a1a; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: rgba(25,25,60,0.7); 
                        padding: 30px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                <h2 style="color: #e8e8f0; margin-bottom: 20px;">Recuperar Contraseña</h2>
                <p style="color: #a0a0c0; margin-bottom: 15px;">Hola <strong>{usuario_nombre}</strong>,</p>
                <p style="color: #a0a0c0; margin-bottom: 20px;">
                    Recibimos una solicitud para recuperar tu contraseña. Haz click en el botón abajo para continuar.
                </p>
                <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #f87171 0%, #fb923c 100%);
                   color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none;
                   font-weight: 600; margin-bottom: 20px;">Recuperar Contraseña</a>
                <p style="color: #6a6a8a; font-size: 12px; margin-top: 20px;">
                    Este link expira en 2 horas.
                </p>
                <p style="color: #6a6a8a; font-size: 12px; margin-top: 10px;">
                    Si no solicitaste esto, puedes ignorar este email.
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(usuario_email, subject, html_body)


def cleanup_expired_tokens():
    """Clean up expired tokens (call periodically from a background job)."""
    query1 = "DELETE FROM password_reset_tokens WHERE expires_at < NOW()"
    query2 = "UPDATE usuarios SET email_token = NULL WHERE email_token_expira < NOW()"
    
    try:
        execute_query(query1, commit=True)
        execute_query(query2, commit=True)
        logger.info("Expired tokens cleaned up")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up tokens: {e}")
        return False
