"""
Paquete para envío de correos electrónicos.

Soporta envío mediante postfix local o relay SMTP externo.

Funciones principales:
- send_email(): Enviar correo con o sin adjuntos
- validar_configuracion(): Validar configuración de email

Example:
    >>> from paquetes.email import send_email
    >>>
    >>> # Envío simple (modo local con postfix)
    >>> result = send_email(
    ...     para='usuario@ejemplo.com',
    ...     titulo='Prueba',
    ...     cuerpo='Mensaje de prueba',
    ...     de='sistema@midominio.com'
    ... )
    >>>
    >>> # Envío con relay externo
    >>> result = send_email(
    ...     para=['user1@ejemplo.com', 'user2@ejemplo.com'],
    ...     titulo='Notificación',
    ...     cuerpo='Contenido del mensaje',
    ...     modo='relay',
    ...     smtp_host='smtp.gmail.com',
    ...     smtp_user='cuenta@gmail.com',
    ...     smtp_password='password'
    ... )
"""

from .email_sender import (
    send_email,
    validar_configuracion
)

__all__ = [
    'send_email',
    'validar_configuracion'
]
