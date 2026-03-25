"""
Logging Configuration for QR Access PRO
Structured logging with JSON format and trace IDs for distributed tracing.
"""
import logging
import structlog
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def setup_logging(app_name="qr_access_pro", log_level=logging.INFO):
    """
    Set up structured logging for the application.
    
    Args:
        app_name: Name of the application
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(
                serializer=lambda obj, chain=None: _custom_json_serializer(obj)
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard Python logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (development friendly)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = LOGS_DIR / f"{app_name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=7,  # Keep 7 days
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (only errors and above)
    error_log_file = LOGS_DIR / f"{app_name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=14,  # Keep 14 days
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Access log file (for request/access logging)
    access_log_file = LOGS_DIR / f"{app_name}_access_{datetime.now().strftime('%Y%m%d')}.log"
    access_handler = RotatingFileHandler(
        access_log_file,
        maxBytes=50 * 1024 * 1024,  # 50MB (more verbose)
        backupCount=30,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(file_formatter)
    
    # Get access logger
    access_logger = logging.getLogger("access")
    access_logger.addHandler(access_handler)
    
    root_logger.info(f"Logging initialized: {app_name}")
    root_logger.info(f"Log directory: {LOGS_DIR}")
    

def _custom_json_serializer(obj):
    """Custom JSON serializer for datetime objects."""
    import json
    from datetime import datetime
    
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)
    
    return json.dumps(obj, cls=DateTimeEncoder, ensure_ascii=False)


def get_logger(name):
    """Get a named logger."""
    return structlog.get_logger(name)


def log_request(method, path, status_code, user_id=None, ip_address=None, duration_ms=None):
    """Log an HTTP request."""
    import uuid
    
    request_id = str(uuid.uuid4())[:8]
    access_logger = logging.getLogger("access")
    
    log_data = {
        "request_id": request_id,
        "method": method,
        "path": path,
        "status_code": status_code,
        "user_id": user_id,
        "ip_address": ip_address,
        "duration_ms": duration_ms,
        "timestamp": datetime.now().isoformat()
    }
    
    access_logger.info(f"Request: {method} {path} - {status_code}", extra=log_data)
    return request_id


def log_auth_event(event_type, user_email, success, ip_address=None, reason=None):
    """Log authentication events."""
    auth_logger = logging.getLogger("auth")
    
    log_data = {
        "event_type": event_type,
        "user_email": user_email,
        "success": success,
        "ip_address": ip_address,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }
    
    level = logging.INFO if success else logging.WARNING
    auth_logger.log(level, f"Auth event: {event_type} - {user_email}: {success}", extra=log_data)


def log_exception(logger_name, exception, context=None):
    """Log an exception with context."""
    logger = logging.getLogger(logger_name)
    
    log_data = {
        "exception": str(exception),
        "exception_type": type(exception).__name__,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.exception(f"Exception in {logger_name}", extra=log_data)


# Access logger shortcut
access_logger = logging.getLogger("access")
auth_logger = logging.getLogger("auth")
