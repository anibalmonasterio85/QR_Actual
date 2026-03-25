# ABOUT QR_Access_PRO

## ¿Qué es QR_Access_PRO?
QR_Access_PRO es un sistema integral y profesional de control de acceso diseñado para gestionar la entrada y salida de personal mediante la validación de códigos QR seguros. Está compuesto por dos partes principales:

1. **Un Panel Web (Backend/Frontend):** Desarrollado en Python con Flask. Administra usuarios, regenera códigos QR, registra el historial de accesos y proporciona métricas operativas y reportes. Cuenta con un robusto Control de Acceso Basado en Roles (RBAC).
2. **Un Sistema de Escaneo (Frontend de Hardware):** Un script adaptable diseñado para estar en la puerta de acceso, conectarse a una cámara o un escáner físico y validar los códigos QR contra la base de datos MySQL en tiempo real utilizando visión por computadora (OpenCV y pyzbar).

## ¿Para qué sirve?
Sirve para reemplazar las tradicionales tarjetas magnéticas, llaves físicas o registros manuales con una solución digital, segura y automatizada. 

Las principales funciones del sistema incluyen:
- **Autenticación rápida:** Lectura de códigos QR en la entrada de las instalaciones.
- **Gestión centralizada:** Creación, edición y suspensión de usuarios desde una interfaz web amigable con permisos granulares (Admin, Guardia, Usuario).
- **Notificaciones automatizadas:** Envío automático de correos (vía SMTP) con los credenciales en formato QR inline.
- **Trazabilidad total:** Registro inmutable de la fecha, hora exacta y usuario que ingresa o sale de las instalaciones.
- **Seguridad perimetral:** Rate Limiting y *cooldowns* anti-abuso, previniendo accesos e intentos no autorizados.

## ¿Por qué es la mejor opción en el entorno laboral?

### 1. Costo-Efectividad y Escalabilidad
A diferencia de los sistemas biométricos de huellas dactilares o tarjetas NFC que requieren hardware costoso para cada punto de acceso y consumibles (tarjetas físicas), QR_Access_PRO solo requiere un teléfono inteligente en el bolsillo del empleado y una cámara/escáner básica en la puerta. Agregar más empleados tiene un costo adicional Cero.

### 2. Alta Disponibilidad y Tiempos de Respuesta
Concebido bajo una arquitectura robusta (Python + Flask + MySQL), el sistema está optimizado con índices de base de datos estructurales para procesar peticiones de escaneo velozmente sin sufrir latencia, evitando cuellos de botella ("filas o colas") en las entradas.

### 3. Contactless (100% Sin Contacto)
Post-pandemia, es un estándar de higiene laboral. Los empleados simplemente muestran su código desde la pantalla de sus teléfonos, reduciendo el riesgo de desgaste de hardware y transmisión de enfermedades.

### 4. Modularidad y Despliegue
La división del proyecto en Web Panel y Scanner permite despliegues versátiles:
- El escáner puede correr en máquinas independientes o en ordenadores compactos (ej. Raspberry Pi).
- El Panel Web y la Base de Datos pueden alojarse en un servidor local cerrado o llevarse a la nube sin impactar el funcionamiento del escáner.

## Fines y Proyecciones Futuras

El objetivo del sistema en su etapa actual es otorgar control, orden y métricas exactas a las administraciones o departamentos de Recursos Humanos/Seguridad sobre el tráfico físico de la empresa, eliminando la suplantación de identidad mediante la rotación de QRs y un registro auditable sólido.
