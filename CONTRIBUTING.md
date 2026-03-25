# Guía de Contribución - QR Access PRO

Gracias por tu interés en contribuir a QR Access PRO. Este documento proporciona pautas para garantizar calidad, seguridad y consistencia.

## Requisitos Previos

- Python 3.11 o superior
- MySQL 8.0+
- Redis 7.0+ (recomendado)
- Git

## Configuración del Entorno

```bash
# Clonar el repositorio
git clone <repo>
cd QR_Access_PROPC

# Crear virtual environment
python -m venv venv

# Activar virtual environment
# En Windows:
.\venv\Scripts\Activate.ps1
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Proceso de Contribución

### 1. Crear una Rama (Branch)

```bash
# Siempre crear rama desde develop (o main)
git checkout -b feature/tu-feature
# O para bug fixes
git checkout -b fix/tu-bug
```

**Nombres de rama recomendados:**
- `feature/nueva-funcionalidad`
- `fix/nombre-del-bug`
- `refactor/nombre-cambio`
- `docs/mejora-documentacion`
- `test/cobertura-componente`

### 2. Hacer Cambios

#### Estándares de Código

**Python:**
- Usar PEP 8
- Nombres descriptivos en inglés (excepto interfaz de usuario)
- Máximo 120 caracteres por línea
- Type hints cuando sea posible
- Docstrings para funciones públicas

```python
def create_user(nombre: str, correo: str, rol: str = 'usuario') -> int:
    """
    Create a new user.
    
    Args:
        nombre: User's full name
        correo: User's email
        rol: User role (default: 'usuario')
    
    Returns:
        User ID if successful
    
    Raises:
        ValueError: If email already exists
    """
    pass
```

**HTML/CSS:**
- Indentación: 2 espacios
- Usar clases BEM para CSS
- Mantener dark mode consistency
- Mobile-first responsive design

**JavaScript:**
- Comillas simples para strings
- Semicolons requeridos
- Use `const` por defecto, `let` si reasignación
- Funciones arrow cuando sea apropiado

### 3. Testing

**Antes de commit, ejecuta:**

```bash
# Linter
pylint web_panel/ config/ --disable=C0111,C0301

# Type checking
mypy web_panel/ config/

# Tests
pytest tests/ -v --cov=web_panel --cov-report=html

# Verificar cobertura >80%
```

**Crear tests para:**
- Modelos (CRUD operations)
- Rutas críticas (auth, admin)
- Servicios (email, QR)
- Validaciones

```python
def test_create_user_valid():
    """Test creating a valid user."""
    user_id = create_user("John", "john@example.com")
    assert user_id is not None
    
    user = get_by_id(user_id)
    assert user['nombre'] == "John"
    assert user['correo'] == "john@example.com"
```

### 4. Commits

**Mensaje de commit:**
```
<tipo>: <descripción breve>

<descripción detallada si es necesario>

<referencias a issues>
```

**Tipos válidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `refactor`: Mejora de código sin cambiar funcionalidad
- `perf`: Optimización de performance
- `test`: Agregar o mejorar tests
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no alteran funcionalidad)
- `chore`: Cambios en dependencias, configuración

**Ejemplos válidos:**
```
feat: add TOTP dynamic QR support
fix: resolve race condition in access log
refactor: simplify user model queries
docs: update deployment instructions
test: add coverage for email confirmation
```

### 5. Seguridad

**Antes de push:**

```bash
# Escanear vulnerabilidades
safety check

# Verificar secretos
pip install detect-secrets
detect-secrets scan

# NO commitear:
- Contraseñas o API keys
- Datos de usuarios reales
- Tokens o credenciales
```

### 6. Pull Request

**Checklist PR:**

- [ ] Nombrar rama según convención
- [ ] Tests pasan: `pytest`
- [ ] Cobertura >80%: `coverage report`
- [ ] Linting pasa: `pylint`
- [ ] Sin secretos expuestos
- [ ] Documentación actualizada
- [ ] Cambios en `CHANGELOG.md`
- [ ] Commits atómicos con mensajes claros

**Descripción PR:**

```markdown
## Descripción
Breve resumen de lo que hace este PR.

## Tipo de cambio
- [ ] Nueva funcionalidad
- [ ] Corrección de bug
- [ ] Cambio que requiere update de documentación

## Cómo testearlo
Instrucciones para verificar funcionalmente.

## Checklist
- [ ] Código sigue los estándares del proyecto
- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] Sin breaking changes
```

## Mejores Prácticas

### Seguridad
- **Siempre** validar inputs de usuario
- Usar prepared statements para queries SQL
- Hash de contraseñas con Scrypt (werkzeug)
- Rate limiting en endpoints críticos
- CORS restrictivo

### Performance
- Usar índices en queries frecuentes
- Cacheo Redis para datos repetidos
- Paginación para tablas grandes
- Lazy loading cuando sea posible

### Mantenibilidad
- Documentar código complejo
- Refactorizar código duplicado
- Mantener separación de responsabilidades
- Usar constantes para "magic numbers"

### Testing
- Escribir tests ANTES de features (TDD)
- Fixtures para datos de test
- Mocks para dependencias externas
- Cobertura mínima 80%

## Áreas de Desarrollo Prioritario

1. **QRs Dinámicos (TOTP)** - Validación mejorada
2. **Módulo de Nómina** - Cálculos de horas
3. **Geolocalización** - IP location mapping
4. **Biometría** - Face recognition opcional
5. **SaaS/Multi-tenant** - Modelos de negocio

## Reporte de Bugs

**Usar el template:**

```markdown
**Descripción**
Descripción clara del bug.

**Pasos para reproducir**
1. ...
2. ...

**Comportamiento esperado**
Qué debería pasar.

**Comportamiento actual**
Qué está pasando.

**Screenshots** (si es UI)

**Entorno**
- OS: 
- Python: 
- Rama: 
- Error log: 
```

## Preguntas?

- Abre un issue para preguntas
- Revisa documentación en `/docs`
- Consulta PRs previos para contexto

## Licencia

Al contribuir, aceptas que tu código sea bajo la misma licencia del proyecto.

---

**Gracias por contribuir a QR Access PRO! 🚀**
