"""
QR Access Control PRO - Settings
Loads environment variables from .env file
"""
import os
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    """Application configuration loaded from environment."""

    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-me')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))

    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3307))
    DB_USER = os.getenv('DB_USER', 'admin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'admin')
    DB_NAME = os.getenv('DB_NAME', 'qr_access')
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))

    # Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@qraccess.com')

    # Application
    APP_NAME = os.getenv('APP_NAME', 'QR Access Control PRO')
    QR_CODES_DIR = os.getenv('QR_CODES_DIR', 'static/qrcodes')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/web_panel.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


config = Config()
