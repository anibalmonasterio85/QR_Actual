# QR Access PRO - Quick Reference Guide

## 🚀 Startup Commands

### Development Local
```bash
# Activate environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # macOS/Linux

# Run debug server
python web_panel/app.py      # Listens on http://localhost:5000
```

### With Docker
```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Database Setup
```bash
# Initialize fresh database
python init_database.py

# Apply schema extensions
mysql -u qr_access -p qr_access_db < schema_extensions.sql

# Backup database
mysqldump -u qr_access -p qr_access_db > backup_$(date +%Y%m%d).sql
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=web_panel --cov-report=html

# Run specific test
pytest tests/test_models.py::TestUserModelPassword::test_hash_password -v

# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Watch mode (auto-run on changes)
pytest-watch tests/
```

## 📁 Project Structure

```
QR_Access_PROPC/
├── web_panel/              # Main Flask application
│   ├── app.py             # Flask app initialization
│   ├── models/            # Database models
│   │   ├── user.py        # User model
│   │   ├── access_log.py  # Access logging
│   │   ├── payroll.py     # Payroll/shifts
│   │   └── zone.py        # Multi-zone RBAC
│   ├── routes/            # Route handlers
│   │   ├── auth.py        # Authentication
│   │   ├── dashboard.py   # User dashboard
│   │   ├── admin.py       # Admin panel
│   │   └── api.py         # API endpoints
│   ├── services/          # Business logic
│   │   ├── qr_service.py
│   │   ├── email_service.py
│   │   ├── totp_service.py
│   │   ├── cache_service.py
│   │   ├── audit_service.py
│   │   └── email_confirmation_service.py
│   ├── static/            # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── qrcodes/
│   └── templates/         # HTML templates
├── config/                # Configuration
│   ├── database.py        # DB connection pool
│   ├── settings.py        # Settings
│   └── logging_config.py  # Logging setup
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest fixtures
│   ├── test_models.py     # Model tests
│   └── test_routes.py     # Route tests
├── logs/                  # Application logs
├── backups/               # Database backups
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image
├── docker-compose.yml     # Docker Compose config
├── nginx.conf             # Nginx config
├── .env.example           # Environment template
└── README.md              # Documentation
```

## 🔧 Common Development Tasks

### Add New Database Model
```python
# 1. Create migration SQL in schema_extensions.sql
# 2. Create model file: web_panel/models/new_model.py
# 3. Import in __init__.py
# 4. Add tests in tests/test_models.py
```

### Create New Route
```python
# 1. Add in web_panel/routes/{module}.py
# 2. Use @bp.route() decorator
# 3. Add tests in tests/test_routes.py
# 4. Document in API docs (if API endpoint)
```

### Add New Service
```python
# 1. Create web_panel/services/new_service.py
# 2. Add functions with docstrings
# 3. Add unit tests in tests/test_services.py
# 4. Import where needed
```

### Database Queries
```python
# Use execute_query from config.database
from config.database import execute_query

# SELECT one
result = execute_query("SELECT * FROM usuarios WHERE id = %s", (1,), fetch_one=True)

# SELECT multiple
results = execute_query("SELECT * FROM usuarios", fetch_all=True)

# INSERT/UPDATE/DELETE
execute_query("INSERT INTO usuarios (nombre, correo) VALUES (%s, %s)", 
              ("John", "john@example.com"), commit=True)
```

## 📊 Key Files Reference

| File | Purpose | Usage |
|------|---------|-------|
| `web_panel/app.py` | Flask app factory | Entry point, blueprint registration |
| `config/database.py` | DB connection pool | Execute all SQL queries |
| `config/logging_config.py` | Logging setup | get_logger(), log_*() functions |
| `web_panel/services/cache_service.py` | Redis cache | get_cache(), set_cache() |
| `web_panel/services/totp_service.py` | TOTP/QR validation | generate_secret(), verify_totp_code() |
| `requirements.txt` | Dependencies | pip install -r requirements.txt |

## 🔐 Security Checklist

- [ ] Never commit `.env` with real values
- [ ] Use `generate_password_hash()` for passwords
- [ ] Validate all user inputs
- [ ] Use prepared statements (parameterized queries)
- [ ] Set HTTPS in production
- [ ] Enable rate limiting
- [ ] Add CSRF tokens to forms
- [ ] Log security events
- [ ] Use secure session cookies

## 🐛 Debugging

### View Logs
```bash
tail -f logs/qr_access_pro_$(date +%Y%m%d).log
tail -f logs/qr_access_pro_errors_$(date +%Y%m%d).log
tail -f logs/qr_access_pro_access_$(date +%Y%m%d).log
```

### Database Issues
```bash
# Connect to MySQL
mysql -u qr_access -p qr_access_db

# Check connection pool status
SHOW PROCESSLIST;

# Check slow queries
SHOW ENGINE INNODB STATUS;
```

### Flask Debug Mode
```python
# In app.py or .env
FLASK_ENV=development
FLASK_DEBUG=1  # Auto-reload on changes
```

### Profiling Performance
```python
from werkzeug.middleware.profiler import ProfilerMiddleware
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[5])
```

## 📦 Dependencies Management

```bash
# Update pip
pip install --upgrade pip

# Add new dependency
pip install package_name
pip freeze > requirements.txt

# Check for vulnerabilities
safety check

# List installed packages
pip list

# Remove unused dependencies
pip clean
```

## 🚀 Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in .env
- [ ] Configure HTTPS certificates
- [ ] Set strong `SECRET_KEY`
- [ ] Enable Redis caching
- [ ] Configure Nginx reverse proxy
- [ ] Set up database backups
- [ ] Configure email service
- [ ] Enable logging
- [ ] Set up monitoring/alerts
- [ ] Test SSL certificate
- [ ] Configure firewall rules
- [ ] Set resource limits in Docker
- [ ] Enable GZIP compression
- [ ] Configure CORS properly

## 🔗 Important URLs

| URL | Purpose | Auth Required |
|-----|---------|---------------|
| `http://localhost:5000` | Dashboard | Yes |
| `http://localhost:5000/login` | Login page | No |
| `http://localhost:5000/register` | Registration | No |
| `http://localhost:5000/admin` | Admin panel | Yes (Admin) |
| `http://localhost:5000/admin/usuarios` | Users management | Yes (Admin) |
| `http://localhost:5000/api/stats` | Statistics API | Yes |
| `http://localhost:5000/api/validate_qr` | QR validation | Yes |
| `http://localhost:5000/api/docs` | API documentation | No |

## 💡 Tips & Tricks

### Flask Shell
```bash
flask shell
>>> from web_panel.models.user import *
>>> users = get_all()
>>> user = get_by_email("test@example.com")
```

### Quick Test Run
```bash
pytest tests/test_models.py -v -s --tb=short
```

### Check Code Style
```bash
pylint web_panel/
black --check web_panel/
flake8 web_panel/
```

### Database Backup & Restore
```bash
# Backup
mysqldump -u qr_access -p qr_access_db > backup.sql

# Restore
mysql -u qr_access -p qr_access_db < backup.sql
```

### Clear Redis Cache
```bash
redis-cli FLUSHDB
```

### Generate Test Data
```bash
python scripts/generate_test_data.py  # If exists
```

## 🆘 Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `Cannot connect to DB` | Check MySQL is running, .env credentials |
| `No module named 'config'` | Run from project root, check PYTHONPATH |
| `Redis connection refused` | Start Redis with `redis-server` |
| `Port 5000 already in use` | `lsof -i :5000` then `kill -9 <PID>` |
| `Static files not loading` | Check file permissions in `web_panel/static/` |
| `Email not sending` | Check .env MAIL_* settings and SMTP access |

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Last Updated:** 2026-03-14
**Version:** 2.0.0
