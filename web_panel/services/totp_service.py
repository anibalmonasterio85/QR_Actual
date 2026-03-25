"""
TOTP Service for QR Access PRO
Generates and validates time-based one-time passwords for dynamic QR codes.
Uses PyOTP for RFC 6238 compliance.
"""
import pyotp
import qrcode
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


def generate_secret():
    """Generate a new TOTP secret key."""
    return pyotp.random_base32()


def get_totp_code(secret):
    """Get current TOTP code for a secret."""
    totp = pyotp.TOTP(secret)
    return totp.now()


def verify_totp_code(secret, code):
    """Verify a TOTP code against a secret."""
    totp = pyotp.TOTP(secret)
    # Allow ±1 time window (±30 seconds) for clock skew
    return totp.verify(code, valid_window=1)


def generate_qr_with_totp(secret, user_name, issuer="QR Access PRO"):
    """Generate a QR code image with TOTP provisioning URI."""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user_name, issuer_name=issuer)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make()
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def generate_dynamic_qr_data(user_qr_code, user_email):
    """Generate dynamic QR data with TOTP validation."""
    SECRET_PREFIX = "QRA"  # QR Access prefix
    
    totp = pyotp.TOTP(user_qr_code[:20])  # Use first 20 chars of QR code as seed
    current_code = totp.now()
    
    # Format: {user_email}:{totp_code}:{timestamp}
    return f"{user_email}:{current_code}:{int(pyotp.time.time())}"


def validate_dynamic_qr(qr_data, stored_qr_secret, time_window=60):
    """
    Validate dynamic QR data with time window tolerance.
    
    Args:
        qr_data: Data extracted from scanned QR (format: email:code:timestamp)
        stored_qr_secret: The user's stored QR secret
        time_window: Seconds to accept (default 60 for ±30s TOTP window)
    
    Returns:
        dict with keys: valid (bool), email (str), error (str if not valid)
    """
    try:
        parts = qr_data.split(":")
        if len(parts) != 3:
            return {"valid": False, "error": "Invalid QR format"}
        
        email, code, timestamp = parts
        timestamp = int(timestamp)
        
        # Check time freshness (within last 60 seconds)
        import time
        current_time = int(time.time())
        if abs(current_time - timestamp) > time_window:
            return {"valid": False, "error": "QR code expired"}
        
        # Verify TOTP code
        totp = pyotp.TOTP(stored_qr_secret[:20])
        if not totp.verify(code, valid_window=1):
            return {"valid": False, "error": "Invalid TOTP code"}
        
        logger.info(f"Dynamic QR validated for {email}")
        return {"valid": True, "email": email}
    
    except Exception as e:
        logger.error(f"Error validating dynamic QR: {e}")
        return {"valid": False, "error": str(e)}
