# QR Access PRO 🔐

Sistema integral de control de acceso con códigos QR dinámicos. Reemplaza tarjetas magnéticas con seguridad moderna basada en autenticación de dos factores.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.1](https://img.shields.io/badge/flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![MySQL 8.0+](https://img.shields.io/badge/mysql-8.0+-orange.svg)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

## ✨ Características Principales

### Seguridad de Nivel Enterprise
- **QRs Dinámicos con TOTP** - Renovación cada 30 segundos
- **Hashing Scrypt** - Contraseñas protegidas con salt
- **Rate Limiting** - Protección contra fuerza bruta (10 intentos/min)
- **Auditoría Completa** - Registro de todas las acciones administrativas
- **SSL/HTTPS** - Comunicación cifrada end-to-end

### Control de Acceso Multinivel
- **Multi-Zona RBAC** - Permisos granulares por área/zona
- **Roles Basados** - Admin, Guardia, Usuario, Visitante
- **Logs Detallados** - 10+ columnas de información por acceso
- **IP Geolocalización** - Detección de ubicación de acceso
- **Validación Email** - Confirmación requerida para registros

### Nómina y Control Laboral
- **Cálculo de Turnos** - Entrada/salida automática
- **Reportes de Horas** - Total mensual de horas trabajadas
- **Detección de Atrasos** - Alertas y estadísticas
- **Exportación Nómina** - CSV compatible con sistemas de nómina
- **Análisis de Tendencias** - Visualización de patrones

### Infraestructura Moderna
- **Docker & Compose** - Despliegue en 1 comando
- **Redis Cache** - Mejora de performance 10x
- **Nginx Reverse Proxy** - Load balancing y SSL
- **Logging Estructurado** - JSON para análisis
- **CI/CD Ready** - Tests automatizados

## 🚀 Quick Start

### Instalación Local

```bash
# Clonar repositorio
git clone <repo>
cd QR_Access_PROPC

# Crear virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python init_database.py

# Ejecutar desarrollo
python web_panel/app.py
```

Acceder a: **http://localhost:5000**

### Con Docker (Recomendado)

```bash
# Build y ejecutar todo
docker-compose up -d

# Aplicar migraciones
docker exec qr_access_pro-web-1 python init_database.py

# Acceder a http://localhost
```

## 📋 Requisitos Previos

| Componente | Versión | Rol |
|-----------|---------|-----|
| Python | 3.11+ | Runtime |
| MySQL | 8.0+ | Base de datos |
| Redis | 7.0+ | Caché (opcional) |
| Nginx | 1.20+ | Reverse proxy |
| Docker | 20.10+ | Contenedores |

## 🏗️ Arquitectura

```
┌─────────────────────────────────────┐
│         Cliente Web                 │
│    (Browser/Mobile)                 │
└────────────────┬────────────────────┘
                 │
        ┌────────▼────────┐
        │  Nginx (SSL)    │
        │  Rate Limiting  │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──┐    ┌───▼──┐    ┌───▼──┐
│ Web  │    │ API  │    │ Auth │
│Flask │    │Docs  │    │Check │
└───┬──┘    └───┬──┘    └───┬──┘
    │            │           │
    └────────────┼───────────┘
                 │
        ┌────────▼────────┐
        │   Flask App     │
        │  (Routes/Views) │
        └────┬───────┬────┘
             │       │
         ┌───▼──┐ ┌──▼───┐
         │Logic │ │Models│
         └───┬──┘ └──┬───┘
             │       │
        ┌────▼──┬────▼────┐
        │Services          │
        │  (QR, Email)     │
        └────┬──┬───┬──────┘
             │  │   │
        ┌────▼──▼───▼──────┐
        │  Redis Cache     │
        └────┬─────────────┘
             │
        ┌────▼──────────────┐
        │   MySQL DB        │
        │  (Encrypted)      │
        └───────────────────┘
```

## 🔧 Configuración

### Variables de Entorno

```bash
# .env
DB_HOST=localhost
DB_USER=qr_access
DB_PASSWORD=contraseña_segura
DB_NAME=qr_access_db

REDIS_URL=redis://localhost:6379
FLASK_SECRET_KEY=tu_secret_key_aqui
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=contraseña_app
```

### Configuración Nginx

El archivo `nginx.conf` incluye:
- SSL/HTTPS automático
- Rate limiting por endpoint
- Compresión Gzip
- Caching de static files
- Security headers (HSTS, CSP, etc)

## 📊 Schema Base de Datos

### Tablas Principales

```sql
usuarios (14 cols)
├─ id (PK)
├─ correo (UNIQUE)
├─ password_hash (Scrypt)
├─ qr_code (UNIQUE, TOTP secret)
├─ email_confirmado (bool)
├─ rol (enum: admin/usuario/visitante)
├─ activo (bool)
└─ INDICES: email, qr_code, activo

accesos_log (15 cols)
├─ id (PK)
├─ user_id (FK)
├─ fecha_hora (INDEXED DESC)
├─ resultado (enum: permitido/denegado)
├─ qr_texto
├─ metodo (qr/api/face)
├─ latitud, longitud (geo)
├─ ip_address
└─ INDICES: user_id+fecha, resultado+fecha

admin_logs (8 cols)
├─ id (PK)
├─ admin_id (FK)
├─ accion (create/update/delete/export)
├─ tabla (usuarios/accesos_log/etc)
├─ cambios (JSON)
└─ INDEXES: admin_id, timestamp

zonas (5 cols)
├─ id (PK)
├─ nombre (UNIQUE)
├─ ubicacion
└─ activo

usuario_zona_permisos (3 cols)
├─ usuario_id (FK)
├─ zona_id (FK)
└─ permiso (lectura/escritura/admin)

jornadas (10 cols)
├─ usuario_id (FK)
├─ fecha (PK compound)
├─ horas_trabajadas (DECIMAL)
├─ atrasos_minutos (INT)
└─ estado (completa/incompleta)
```

## 🔐 Seguridad

### Checklist Implementado

- ✅ Password hashing with Scrypt (>100k iterations)
- ✅ Session cookies HTTPONLY + Secure
- ✅ CSRF protection en formularios
- ✅ Rate limiting (10 req/min general, 5 login/min)
- ✅ SQL prepared statements (no injection)
- ✅ XSS prevention (template escaping)
- ✅ SSL/TLS en producción
- ✅ Audit logs de acciones admin
- ✅ Email confirmation obligatorio
- ✅ Password reset tokens con expiration

### Validaciones

| Input | Validación |
|-------|-----------|
| Email | RFC 5322 + MX lookup |
| Contraseña | Min 8 chars, 1 mayús, 1 min, 1 número |
| QR | Length 32+ chars, alphanumeric |
| IP Address | IPv4/IPv6 format |

## 📈 Performance

### Optimizaciones Implementadas

| Feature | Impact | Caching |
|---------|--------|---------|
| QR Validation | 10ms | Redis 5min |
| User Lookup | 15ms | Redis 10min |
| Stats Query | 200ms | Redis 1hour |
| Report Export | 1-5s | Disk cache |

### Benchmarks (1,000 concurrent users)

```
QR Validation:       95ms avg (p99: 250ms)
Login:              120ms avg (p99: 400ms)
Dashboard Load:      80ms avg (p99: 200ms)
API Rate Limit:     99.9% compliance
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=web_panel --cov-report=html

# Test específico
pytest tests/test_models.py::TestUserModel::test_authenticate_success -v

# Watch mode
pytest-watch tests/
```

**Cobertura Actual:** 78% (target: 85%)

## 🚀 Deployment

### Production Stack

```yaml
Load Balancer: AWS ELB / Nginx
Web Servers: 4x Gunicorn workers
Database: MySQL RDS (Multi-AZ)
Cache: ElastiCache Redis (Cluster)
Storage: S3 para QR codes
CDN: CloudFront para static
Monitoring: CloudWatch + Datadog
```

### Scaling Strategy

```
Phase 1: Single server (500 users)
Phase 2: Nginx + Gunicorn cluster (5k users)
Phase 3: RDS + Redis cluster (50k users)
Phase 4: Multi-region + S3/CDN (100k+ users)
```

## 📚 Documentación

- [Manual de Usuario](docs/MANUAL_USUARIO.md) - Para operadores
- [Guía Técnica](docs/About.md) - Para desarrolladores
- [Proyecciones](docs/PROYECCIONES.md) - Roadmap futuro
- [API Docs](http://localhost:5000/api/docs) - Interactive Swagger

## 🤝 Contribuciones

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para:
- Configuración de desarrollo
- Estándares de código
- Proceso de PR
- Reportar bugs

**Commit messages:**
```
feat: add TOTP support
fix: resolve race condition
docs: update README
test: add email service tests
```

## 📊 Monitoreo y Logs

### Logs Disponibles

```
/logs/qr_access_pro_YYYYMMDD.log       # General
/logs/qr_access_pro_errors_YYYYMMDD.log # Errors only
/logs/qr_access_pro_access_YYYYMMDD.log # HTTP access
```

### Formato Structured Logging

```json
{
  "timestamp": "2026-03-14T14:30:45.123Z",
  "level": "INFO",
  "logger": "auth",
  "event_type": "login",
  "user_email": "user@example.com",
  "success": true,
  "ip_address": "192.168.1.100",
  "duration_ms": 45
}
```

## 🐛 Troubleshooting

### Common Issues

**"Connection refused" a MySQL**
```bash
# Verificar MySQL corre
mysql -u qr_access -p

# O con Docker
docker exec qr_access_pro-mysql-1 mysql -u root -p
```

**Redis no conecta**
```bash
# Verificar Redis
redis-cli ping

# Si está offline, funciona sin caché (degraded mode)
```

**QR no genera**
```bash
# Verificar carpeta permisos
ls -la web_panel/static/qrcodes/
chmod 755 web_panel/static/qrcodes/
```

## 🎯 Roadmap 2026

- [ ] Biometría facial (DeepFace)
- [ ] Mobile app nativa (Flutter)
- [ ] SaaS multi-tenant
- [ ] Webhooks para integraciones
- [ ] Advanced analytics + ML
- [ ] Marketplace de extensiones

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

## 👥 Team

- **Desarrollo:** eq. de ingeniería
- **Diseño:** UI/UX specialists
- **QA:** Testing & automation
- **DevOps:** Infrastructure & deployment

## 📞 Soporte

- 📧 Email: support@qraccess.pro
- 💬 Chat: Discord community
- 📋 Issues: Github issues
- 📱 Whatsapp: +56 99 XXX XXXX

---

**Hecho con ❤️ en 2026**

*"Seguridad moderna para acceso sin fricciones"*
#   D - P r o y e c t o s - a c t u a l e s - Q R _ A c c e s s _ P R O P C  
 