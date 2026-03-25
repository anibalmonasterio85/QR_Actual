"""
Pytest configuration and fixtures for QR Access PRO
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    from web_panel.app import app as flask_app
    
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    return flask_app


@pytest.fixture
def client(app):
    """Test client for Flask app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test runner for CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """Application context for tests."""
    with app.app_context():
        yield app


class TestConfig:
    """Test configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    RATE_LIMIT_ENABLED = False


@pytest.fixture
def mock_db():
    """Mock database for unit tests."""
    import unittest.mock as mock
    
    # Mock execute_query function
    with mock.patch('config.database.execute_query') as mock_query:
        yield mock_query


@pytest.fixture
def mock_email():
    """Mock email service."""
    import unittest.mock as mock
    
    with mock.patch('web_panel.services.email_service.send_email') as mock_send:
        mock_send.return_value = True
        yield mock_send


@pytest.fixture
def mock_redis():
    """Mock Redis cache."""
    import unittest.mock as mock
    
    with mock.patch('web_panel.services.cache_service.cache') as mock_cache:
        yield mock_cache


@pytest.fixture
def sample_user():
    """Sample user data for tests."""
    return {
        'id': 1,
        'nombre': 'Test User',
        'correo': 'test@example.com',
        'password_hash': 'hashed_password',
        'rol': 'usuario',
        'activo': True,
        'qr_code': 'test_qr_code_12345678901234567890',
        'fecha_expiracion': None,
        'creado_en': '2026-03-14 12:00:00'
    }


@pytest.fixture
def sample_admin():
    """Sample admin user data for tests."""
    return {
        'id': 2,
        'nombre': 'Admin User',
        'correo': 'admin@example.com',
        'password_hash': 'hashed_password',
        'rol': 'admin',
        'activo': True,
        'qr_code': 'admin_qr_code_12345678901234567890',
        'fecha_expiracion': None,
        'creado_en': '2026-03-14 12:00:00'
    }


@pytest.fixture
def sample_access_log():
    """Sample access log entry for tests."""
    return {
        'id': 1,
        'user_id': 1,
        'fecha_hora': '2026-03-14 12:30:00',
        'qr_texto': 'test_qr_code',
        'resultado': 'permitido',
        'metodo': 'qr',
        'scanner_id': 'scanner_1',
        'ip_address': '192.168.1.100'
    }


@pytest.fixture
def authenticated_user(client):
    """Fixture for authenticated user session."""
    # Login user if your app has auth
    response = client.post('/login', data={
        'correo': 'test@example.com',
        'password': 'password123'
    })
    
    return {
        'client': client,
        'status_code': response.status_code
    }


@pytest.mark.usefixtures("app_context")
class TestBase:
    """Base class for tests with app context."""
    pass


# Pytest hooks
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add markers based on test names
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "auth" in item.nodeid:
            item.add_marker(pytest.mark.auth)
