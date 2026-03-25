"""
QR Access Control PRO - Flask Application Entry Point
Initializes Flask, Flask-Mail, Flask-Limiter, registers blueprints, configures logging.
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, redirect, url_for
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.settings import config

# Global instances — imported by routes
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)


def create_app():
    """Application factory."""
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

    # Configuration
    app.secret_key = config.SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    # Mail config
    app.config['MAIL_SERVER'] = config.MAIL_SERVER
    app.config['MAIL_PORT'] = config.MAIL_PORT
    app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER

    # Initialize Flask-Mail
    mail.init_app(app)

    # Ensure directories exist
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'backups'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'qrcodes'), exist_ok=True)

    # Setup logging
    setup_logging(app)

    # Register blueprints
    from web_panel.routes.auth import auth_bp
    from web_panel.routes.dashboard import dashboard_bp
    from web_panel.routes.admin import admin_bp
    from web_panel.routes.api import api_bp
    from web_panel.routes.scanner import scanner_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(scanner_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return redirect(url_for('dashboard.index'))

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal Server Error: {e}")
        return "<h1>Error interno del servidor</h1><p>Por favor, contacte al administrador.</p>", 500

    # Initialize default admin user
    init_admin_user(app)

    app.logger.info(f"🚀 {config.APP_NAME} initialized successfully")

    return app


def setup_logging(app):
    """Configure logging: rotated file + console output."""
    log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    log_format = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'

    # File handler (rotating)
    log_file = os.path.join(BASE_DIR, config.LOG_FILE)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))

    # Apply to Flask app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    # Apply to root logger (for models/services that use logging.getLogger)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)


def init_admin_user(app):
    """Create default admin user if none exists."""
    try:
        from web_panel.models import user as user_model
        admin = user_model.get_by_email('admin@qraccess.com')
        if not admin:
            user_id = user_model.create_user(
                nombre='Administrador',
                correo='admin@qraccess.com',
                password='admin123',
                rol='admin'
            )
            # Generate QR for admin
            from web_panel.services import qr_service
            admin = user_model.get_by_id(user_id)
            if admin and admin.get('qr_code'):
                qr_service.generate_qr_image(admin['qr_code'])
            app.logger.info(f"✅ Admin user created: admin@qraccess.com / admin123")
            print("\n" + "=" * 50)
            print("  ✅ USUARIO ADMIN CREADO")
            print("  📧 Correo: admin@qraccess.com")
            print("  🔑 Contraseña: admin123")
            print("  ⚠️  ¡Cambia la contraseña en producción!")
            print("=" * 50 + "\n")
    except Exception as e:
        app.logger.warning(f"Could not initialize admin user: {e}")
        print(f"⚠️  No se pudo crear el admin: {e}")
        print("   Asegúrate de que la base de datos está inicializada.")
        print(f"   Ejecuta: setup_database.sql en MySQL (puerto {config.DB_PORT})")


# ── Run ──────────────────────────────────
if __name__ == '__main__':
    app = create_app()
    print(f"\n🔐 {config.APP_NAME}")
    print(f"🌐 Servidor: http://localhost:{config.PORT}")
    print(f"📊 Debug: {config.DEBUG}")
    print(f"💾 Base de datos: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    print(f"📁 Logs: {config.LOG_FILE}\n")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
