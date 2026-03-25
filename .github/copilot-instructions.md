---
description: "Instrucciones específicas para el desarrollo del proyecto QR Access PRO - Sistema de control de acceso con códigos QR. Aplica mejores prácticas de seguridad, escalabilidad y mantenibilidad."
applyTo: "**/*.{py,html,css,js,sql}"
---

# Instrucciones para el Desarrollo de QR Access PRO

## Visión General
QR Access PRO es un sistema integral de control de acceso que reemplaza tarjetas magnéticas con códigos QR dinámicos. El proyecto consta de un panel web Flask y un sistema de escaneo físico.

## Principios de Desarrollo

### 1. Seguridad Primero
- **Siempre** usar hashing Scrypt para contraseñas (ya implementado)
- Validar inputs en todos los endpoints
- Implementar rate limiting (ya en auth)
- Usar HTTPS en producción
- Evitar SQL injection con prepared statements

### 2. Código Limpio y Modular
- Mantener separación de responsabilidades: routes, models, services
- Usar nombres descriptivos en inglés
- Documentar funciones con docstrings
- Evitar código duplicado

### 3. Base de Datos
- Usar pool de conexiones (ya configurado)
- Crear índices apropiados para queries frecuentes
- Validar foreign keys
- Backup regular de datos

### 4. UI/UX
- Mantener diseño dark mode consistente
- Usar gradientes y animaciones sutiles
- Responsive design para móviles
- Mensajes de error claros en español

### 5. Testing
- Escribir tests para modelos y rutas críticas
- Usar pytest con fixtures
- Cobertura mínima del 80%

### 6. Logging
- Registrar accesos permitidos/denegados
- Logs de errores con stack traces
- Rotación diaria de logs

## Mejoras Prioritarias
1. Implementar QRs dinámicos (TOTP)
2. Añadir confirmación de email
3. Dockerización
4. Testing automatizado
5. Módulo de turnos y nómina

## Estándares de Commit
- Usar mensajes en inglés
- Formato: "feat: add TOTP support" o "fix: resolve login rate limit bug"
- Commits atómicos por feature

## Dependencias
- Mantener requirements.txt actualizado
- Usar versiones pinned
- Revisar vulnerabilidades con safety

## Deployment
- Configurar variables de entorno
- Usar Gunicorn en producción
- Configurar reverse proxy con SSL