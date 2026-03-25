#!/usr/bin/env python3
"""
QR Access PRO - Environment Setup Script
Initializes and configures the project for development or production.
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Print colored header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def print_info(text):
    """Print info message."""
    print(f"ℹ️  {text}")


def check_python_version():
    """Check if Python version is 3.11+."""
    print_info("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_error(f"Python 3.11+ required. You have {version.major}.{version.minor}")
        sys.exit(1)
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")


def setup_virtual_environment():
    """Create and activate virtual environment."""
    print_info("Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_info("Virtual environment already exists")
    else:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_success("Virtual environment created")


def install_dependencies():
    """Install Python dependencies."""
    print_info("Installing dependencies...")
    
    # Determine pip executable
    if sys.platform == "win32":
        pip = Path("venv/Scripts/pip.exe")
    else:
        pip = Path("venv/bin/pip")
    
    subprocess.run([str(pip), "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip), "install", "-r", "requirements.txt"], check=True)
    
    print_success("Dependencies installed")


def create_env_file():
    """Create .env file if it doesn't exist."""
    print_info("Checking .env file...")
    
    env_path = Path(".env")
    
    if env_path.exists():
        print_info(".env file already exists")
        return
    
    env_content = """# QR Access PRO - Environment Configuration
# Fill in your values here

# Database
DB_HOST=localhost
DB_USER=qr_access
DB_PASSWORD=change_me_in_production
DB_NAME=qr_access_db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Flask
FLASK_APP=web_panel/app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here-change-in-production

# Email Configuration (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@qraccess.pro

# Security
SESSION_TIMEOUT=28800  # 8 hours in seconds
RATE_LIMIT_ENABLED=True

# QR Configuration
QR_SECRET_PREFIX=QRA
QR_ERROR_CORRECTION=HIGH

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=structured

# Environment Type
ENVIRONMENT=development
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print_success(".env file created - PLEASE CONFIGURE IT!")


def create_log_directories():
    """Create log directories."""
    print_info("Setting up log directories...")
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create initial log files
    (log_dir / ".gitkeep").touch()
    
    print_success("Log directories ready")


def create_qr_directory():
    """Create QR code storage directory."""
    print_info("Setting up QR code directory...")
    
    qr_dir = Path("web_panel/static/qrcodes")
    qr_dir.mkdir(parents=True, exist_ok=True)
    
    # Create .gitkeep to preserve directory
    (qr_dir / ".gitkeep").touch()
    
    print_success("QR directory ready")


def create_schemas_table():
    """Print migration reminder."""
    print_header("Database Setup")
    
    print_info("To set up the database, run:")
    print("\n  python init_database.py")
    print("\nThis will create all tables and indexes.")
    
    print_info("\nFor additional features, apply:")
    print("\n  mysql -u qr_access -p qr_access_db < schema_extensions.sql")


def verify_installations():
    """Verify key installations."""
    print_header("Verification")
    
    # Python packages
    try:
        import flask
        print_success(f"Flask {flask.__version__} installed")
    except ImportError:
        print_error("Flask not installed")
    
    try:
        import mysql.connector
        print_success("MySQL connector installed")
    except ImportError:
        print_info("MySQL connector not found (install if needed)")
    
    try:
        import redis
        print_success("Redis installed")
    except ImportError:
        print_info("Redis not installed (optional, but recommended)")
    
    try:
        import pyotp
        print_success("PyOTP (TOTP) installed")
    except ImportError:
        print_error("PyOTP not installed")


def create_startup_script():
    """Create development startup script."""
    print_info("Creating startup script...")
    
    if sys.platform == "win32":
        script_path = Path("start_dev.ps1")
        content = """# QR Access PRO - Development Server
.\\venv\\Scripts\\Activate.ps1
python web_panel/app.py
"""
        script_path.write_text(content)
        print_success("Created start_dev.ps1")
    else:
        script_path = Path("start_dev.sh")
        content = """#!/bin/bash
# QR Access PRO - Development Server
source venv/bin/activate
python web_panel/app.py
"""
        script_path.write_text(content)
        os.chmod(script_path, 0o755)
        print_success("Created start_dev.sh")


def print_next_steps():
    """Print next steps after setup."""
    print_header("Setup Complete! 🎉")
    
    print_info("Next steps:")
    print("""
1. Configure .env file with your settings:
   nano .env  (or use your editor)

2. Set up the database:
   python init_database.py

3. (Optional) Apply schema extensions:
   mysql -u qr_access -p qr_access_db < schema_extensions.sql

4. Start development server:
""")
    
    if sys.platform == "win32":
        print("   .\\start_dev.ps1")
    else:
        print("   ./start_dev.sh")
    
    print(f"""
5. Access the application:
   http://localhost:5000

6. Default credentials:
   Email: admin@example.com
   Password: (set during DB init)

📚 Documentation:
   - README.md - Project overview
   - CONTRIBUTING.md - Development guide
   - docs/MANUAL_USUARIO.md - User manual
   - docs/ - Additional documentation

🆘 Troubleshooting:
   Check logs in: {Path('logs').absolute()}

💡 Tips:
   - Use Redis for better performance
   - Enable HTTPS in production
   - Configure email properly for notifications
   - Run tests before committing: pytest tests/

Happy coding! 🚀
""")


def main():
    """Main setup function."""
    print_header("QR Access PRO - Environment Setup")
    
    try:
        check_python_version()
        setup_virtual_environment()
        install_dependencies()
        create_env_file()
        create_log_directories()
        create_qr_directory()
        create_startup_script()
        verify_installations()
        create_schemas_table()
        print_next_steps()
        
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
