"""
QR Access Control PRO - QR Code Service
Generates QR code images from tokens.
"""
import os
import qrcode
from PIL import Image

# Base directory for QR codes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QR_DIR = os.path.join(BASE_DIR, 'static', 'qrcodes')


def ensure_qr_dir():
    """Ensure the QR codes directory exists."""
    os.makedirs(QR_DIR, exist_ok=True)


def generate_qr_image(token, filename=None):
    """
    Generate a QR code image from a token string.
    Returns the filename of the generated image.
    """
    ensure_qr_dir()

    if filename is None:
        filename = f"qr_{token[:16]}.png"

    filepath = os.path.join(QR_DIR, filename)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1a1a2e", back_color="white")
    img.save(filepath)

    return filename


def get_qr_path(filename):
    """Get the full path to a QR code image."""
    return os.path.join(QR_DIR, filename)


def delete_qr_image(filename):
    """Delete a QR code image."""
    filepath = os.path.join(QR_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
