#!/usr/bin/env python3
"""
QR Access PRO - Health Check Script
Validates project setup and dependencies.
"""
import sys
import subprocess
from pathlib import Path

# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))


def print_check(status, message):
    """Print check result."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")
    return status


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print_check(True, f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_check(False, f"Python 3.11+ required (have {version.major}.{version.minor})")
        return False


def check_venv():
    """Check if virtual environment is activated."""
    in_venv = sys.prefix != sys.base_prefix
    print_check(in_venv, "Virtual environment" + (" activated" if in_venv else " NOT activated"))
    return in_venv


def check_dependencies():
    """Check if required dependencies are installed."""
    required = {
        'flask': 'Flask',
        'mysql.connector': 'MySQL Connector',
        'qrcode': 'QRCode',
        'cv2': 'OpenCV',
        'pyotp': 'PyOTP',
        'structlog': 'Structlog',
        'pytest': 'Pytest',
    }
    
    optional = {
        'redis': 'Redis (recommended)',
        'dotenv': 'Python-dotenv',
    }
    
    print("\n📦 Required Dependencies:")
    all_good = True
    for module, name in required.items():
        try:
            __import__(module)
            print_check(True, f"{name}")
        except ImportError:
            print_check(False, f"{name} - MISSING")
            all_good = False
    
    print("\n📦 Optional Dependencies:")
    for module, name in optional.items():
        try:
            __import__(module)
            print_check(True, f"{name} (installed)")
        except ImportError:
            print_check(False, f"{name} (not installed)")
    
    return all_good


def check_project_structure():
    """Check project directory structure."""
    print("\n📁 Project Structure:")
    
    required_dirs = [
        'web_panel',
        'web_panel/models',
        'web_panel/routes',
        'web_panel/services',
        'web_panel/static',
        'web_panel/templates',
        'config',
        'tests',
        'logs',
    ]
    
    all_good = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        print_check(exists, dir_path)
        all_good = all_good and exists
    
    return all_good


def check_required_files():
    """Check required configuration files."""
    print("\n📄 Configuration Files:")
    
    required_files = {
        'requirements.txt': 'Dependencies',
        'README.md': 'Documentation',
        '.gitignore': 'Git ignore',
        'pytest.ini': 'Pytest config',
        '.env': 'Environment (create from .env.example)',
    }
    
    all_good = True
    for filename, description in required_files.items():
        exists = Path(filename).exists()
        symbol = "✅" if exists else "⚠️"
        print(f"{symbol} {description} ({filename})")
        if filename != '.env' and not exists:
            all_good = False
    
    return all_good


def check_database_connection():
    """Check database connection."""
    print("\n🗄️ Database:")
    
    try:
        from config.database import execute_query
        
        # Try to get pool info without actual query
        try:
            result = execute_query("SELECT 1", fetch_one=True)
            if result:
                print_check(True, "MySQL connection OK")
                return True
            else:
                print_check(False, "MySQL connection failed")
                return False
        except Exception as e:
            print_check(False, f"MySQL error: {str(e)[:50]}")
            return False
    except ImportError:
        print_check(False, "Could not import database config")
        return False


def check_redis_connection():
    """Check Redis connection."""
    print("\n💾 Redis Cache:")
    
    try:
        from services.cache_service import is_redis_available
        
        available = is_redis_available()
        print_check(available, "Redis connection" + (" OK" if available else " (optional)"))
        return available
    except ImportError:
        print_check(False, "Could not import cache service")
        return False


def check_tests():
    """Run basic test suite."""
    print("\n🧪 Tests:")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v', '--co', '-q'],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output_lines = result.stdout.decode().split('\n')
            # Count tests
            test_count = len([l for l in output_lines if '::test_' in l])
            print_check(True, f"Pytest working ({test_count} tests found)")
            return True
        else:
            print_check(False, "Pytest collection failed")
            return False
    except Exception as e:
        print_check(False, f"Pytest error: {str(e)}")
        return False


def check_static_files():
    """Check static files."""
    print("\n📦 Static Files:")
    
    static_dir = Path('web_panel/static')
    
    if static_dir.exists():
        print_check(True, "Static directory exists")
        
        # Check subdirectories
        for subdir in ['css', 'js']:
            subpath = static_dir / subdir
            exists = subpath.exists()
            print_check(exists, f"  └─ {subdir}/" + (f" ({len(list(subpath.glob('*')))} files)" if exists else ""))
        
        return True
    else:
        print_check(False, "Static directory not found")
        return False


def check_environment_file():
    """Check .env file."""
    print("\n⚙️ Environment Configuration:")
    
    env_path = Path('.env')
    env_example = Path('.env.example')
    
    if env_path.exists():
        print_check(True, ".env file exists")
        return True
    elif env_example.exists():
        print_check(False, ".env file not found (copy from .env.example)")
        print("\n  To create: cp .env.example .env")
        print("  Then edit .env with your settings")
        return False
    else:
        print_check(False, "No .env or .env.example found")
        return False


def main():
    """Run all health checks."""
    print("=" * 60)
    print("  QR Access PRO - Health Check")
    print("=" * 60)
    
    results = {
        "Python Version": check_python_version(),
        "Virtual Environment": check_venv(),
        "Dependencies": check_dependencies(),
        "Project Structure": check_project_structure(),
        "Configuration Files": check_required_files(),
        "Database": check_database_connection(),
        "Redis": check_redis_connection(),
        "Tests": check_tests(),
        "Static Files": check_static_files(),
        "Environment": check_environment_file(),
    }
    
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    
    for check_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Ready to develop.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
