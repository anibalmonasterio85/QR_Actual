"""
QR Access Control PRO - Email Service
Sends QR code emails with inline image display and professional HTML template.
Uses Flask-Mail for SMTP. Credentials must be set in .env.
"""
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)


def send_qr_email(mail, recipient_email, recipient_name, qr_image_path):
    """
    Send a professional email with the QR code embedded inline (CID) AND as attachment.
    The QR appears visually inside the email body on all major clients.

    Args:
        mail: Flask-Mail instance (from web_panel.app import mail)
        recipient_email: Destination email address
        recipient_name: Recipient's display name
        qr_image_path: Absolute path to the QR PNG file

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        from flask_mail import Message

        msg = Message(
            subject='🔐 Tu Código QR de Acceso — QR Access Control PRO',
            recipients=[recipient_email]
        )

        # Professional HTML with inline CID image reference
        msg.html = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0f0f1a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f1a;padding:30px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                       border-radius:16px 16px 0 0;padding:36px 40px;text-align:center;">
          <div style="font-size:2.5rem;margin-bottom:8px;">🔐</div>
          <h1 style="color:#fff;margin:0;font-size:1.6rem;font-weight:700;letter-spacing:-0.5px;">
            QR Access Control PRO
          </h1>
          <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:0.9rem;">
            Sistema de Control de Acceso
          </p>
        </td></tr>

        <!-- Body -->
        <tr><td style="background:#1a1a2e;padding:36px 40px;">
          <h2 style="color:#e2e8f0;font-size:1.2rem;margin:0 0 12px;">
            Hola, {recipient_name} 👋
          </h2>
          <p style="color:#94a3b8;line-height:1.6;margin:0 0 24px;">
            Tu código QR de acceso ha sido generado exitosamente.<br>
            Preséntalo ante el escáner para ingresar a las instalaciones.
          </p>

          <!-- QR Code centered inline -->
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr><td align="center" style="padding:20px 0;">
              <div style="background:#fff;display:inline-block;padding:16px;
                          border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,0.4);">
                <img src="cid:qr_code_image" alt="Tu Código QR"
                     width="220" height="220"
                     style="display:block;border-radius:8px;" />
              </div>
            </td></tr>
          </table>

          <p style="color:#64748b;font-size:0.82rem;text-align:center;margin:16px 0 0;">
            ⚠️ No compartas este código. Es personal e intransferible.
          </p>
        </td></tr>

        <!-- Footer -->
        <tr><td style="background:#0f0f1a;border-radius:0 0 16px 16px;
                       padding:20px 40px;text-align:center;border-top:1px solid #2d2d4e;">
          <p style="color:#475569;font-size:0.78rem;margin:0;">
            QR Access Control PRO &bull; Sistema automatizado de control de acceso
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
        """

        # Attach QR as both inline (CID) and downloadable attachment
        if qr_image_path and os.path.exists(qr_image_path):
            with open(qr_image_path, 'rb') as qr_file:
                qr_data = qr_file.read()

            # Inline CID attachment (shows in body)
            msg.attach(
                "mi_codigo_qr.png",
                "image/png",
                qr_data,
                disposition="inline",
                headers={"Content-ID": "<qr_code_image>"}
            )

            # Also attach as downloadable file
            msg.attach(
                "mi_codigo_qr_descarga.png",
                "image/png",
                qr_data,
                disposition="attachment"
            )
        else:
            logger.warning(f"QR image not found at path: {qr_image_path}")

        mail.send(msg)
        logger.info(f"✅ QR email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send QR email to {recipient_email}: {e}", exc_info=True)
        return False


def send_test_email(mail, recipient_email):
    """
    Send a simple test email to verify SMTP configuration.
    Use from Python shell to diagnose email issues without registering a user.

    Usage:
        from web_panel.app import create_app, mail
        app = create_app()
        with app.app_context():
            from web_panel.services.email_service import send_test_email
            send_test_email(mail, 'youraddress@gmail.com')
    """
    try:
        from flask_mail import Message
        msg = Message(
            subject='✅ Test de Correo — QR Access Control PRO',
            recipients=[recipient_email],
            body=(
                'Este es un correo de prueba del sistema QR Access Control PRO.\n'
                'Si recibes este mensaje, la configuración SMTP está correcta.\n\n'
                '— Sistema QR Access Control PRO'
            )
        )
        mail.send(msg)
        logger.info(f"✅ Test email sent to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Test email failed: {e}", exc_info=True)
        return False
