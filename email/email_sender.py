"""
Módulo para envío de correos electrónicos.

Soporta dos modos de operación:
- 'local': Envío directo usando postfix local (localhost:25)
- 'relay': Envío mediante servidor SMTP externo con autenticación

Funcionalidades:
- Envío de correos con o sin adjuntos
- Soporte para múltiples destinatarios
- HTML y texto plano
- Configuración flexible por parámetros o variables de entorno
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Union


def send_email(
    para: Union[str, List[str]],
    titulo: str,
    cuerpo: str = "",
    de: Optional[str] = None,
    adjuntos: Optional[List[str]] = None,
    html: bool = True,
    modo: Optional[str] = None,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    smtp_use_tls: Optional[bool] = None,
    smtp_use_ssl: Optional[bool] = None
) -> dict:
    """
    Envía un correo electrónico con soporte para postfix local o relay externo.

    Args:
        para: Destinatario o lista de destinatarios (emails)
        titulo: Asunto del correo
        cuerpo: Cuerpo del mensaje (opcional, default: "")
        de: Remitente (opcional, usa EMAIL_FROM del .env si no se especifica)
        adjuntos: Lista de rutas de archivos a adjuntar (opcional)
        html: Si True, el cuerpo se interpreta como HTML; si False, texto plano (default: True)
        modo: 'local' para postfix local, 'relay' para SMTP externo
              (opcional, usa EMAIL_MODE del .env, default: 'local')
        smtp_host: Servidor SMTP para modo relay (opcional, usa SMTP_HOST del .env)
        smtp_port: Puerto SMTP (opcional, usa SMTP_PORT del .env, default: 587 para TLS, 465 para SSL, 25 para local)
        smtp_user: Usuario SMTP para autenticación (opcional, usa SMTP_USER del .env)
        smtp_password: Contraseña SMTP (opcional, usa SMTP_PASSWORD del .env)
        smtp_use_tls: Usar STARTTLS (opcional, usa SMTP_USE_TLS del .env, default: True para relay)
        smtp_use_ssl: Usar SSL/TLS directo (opcional, usa SMTP_USE_SSL del .env, default: False)

    Returns:
        dict: {'success': bool, 'message': str, 'destinatarios': list}

    Raises:
        ValueError: Si faltan parámetros requeridos según el modo

    Example (modo local - postfix):
        >>> # Envío simple
        >>> result = send_email(
        ...     para='usuario@ejemplo.com',
        ...     titulo='Prueba',
        ...     cuerpo='Mensaje de prueba',
        ...     de='sistema@midominio.com'
        ... )
        >>> print(result['success'])
        True

    Example (modo relay - SMTP externo):
        >>> # Con servidor externo
        >>> result = send_email(
        ...     para=['user1@ejemplo.com', 'user2@ejemplo.com'],
        ...     titulo='Notificación',
        ...     cuerpo='<h1>Hola</h1><p>Mensaje HTML</p>',
        ...     html=True,
        ...     modo='relay',
        ...     smtp_host='smtp.gmail.com',
        ...     smtp_port=587,
        ...     smtp_user='mi_cuenta@gmail.com',
        ...     smtp_password='mi_password'
        ... )

    Example (con adjuntos):
        >>> result = send_email(
        ...     para='cliente@ejemplo.com',
        ...     titulo='Factura',
        ...     cuerpo='Adjunto encontrará su factura',
        ...     adjuntos=['/ruta/factura.pdf', '/ruta/recibo.pdf']
        ... )

    Variables de entorno (opcionales):
        - EMAIL_MODE: 'local' o 'relay' (default: 'local')
        - EMAIL_FROM: Email del remitente por defecto
        - SMTP_HOST: Servidor SMTP (requerido para modo relay)
        - SMTP_PORT: Puerto SMTP (default: 25 local, 587 relay)
        - SMTP_USER: Usuario SMTP
        - SMTP_PASSWORD: Contraseña SMTP
        - SMTP_USE_TLS: 'true' o 'false' (default: 'true' para relay)
        - SMTP_USE_SSL: 'true' o 'false' (default: 'false')
    """
    # Configuración del modo
    modo = modo or os.getenv('EMAIL_MODE', 'local')

    # Configuración del remitente
    de = de or os.getenv('EMAIL_FROM')
    if not de:
        raise ValueError('El parámetro "de" es requerido o debe estar configurado EMAIL_FROM en .env')

    # Agregar dominio por defecto si no tiene @
    if '@' not in de:
        de = f'{de}@smtp.local'

    # Normalizar destinatarios a lista
    if isinstance(para, str):
        para = [para]

    # Validar destinatarios
    if not para or len(para) == 0:
        raise ValueError('Debe especificar al menos un destinatario en "para"')

    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = de
    msg['To'] = ', '.join(para)
    msg['Subject'] = titulo

    # Adjuntar cuerpo
    if cuerpo:
        mime_type = 'html' if html else 'plain'
        msg.attach(MIMEText(cuerpo, mime_type, 'utf-8'))

    # Adjuntar archivos si existen
    if adjuntos:
        for archivo_path in adjuntos:
            if not os.path.exists(archivo_path):
                return {
                    'success': False,
                    'message': f'Archivo no encontrado: {archivo_path}',
                    'destinatarios': para
                }

            with open(archivo_path, 'rb') as archivo:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(archivo.read())
                encoders.encode_base64(parte)
                nombre_archivo = os.path.basename(archivo_path)
                parte.add_header('Content-Disposition', f'attachment; filename= {nombre_archivo}')
                msg.attach(parte)

    # Enviar según modo
    try:
        if modo == 'local':
            # Modo local: usar postfix en localhost:25
            smtp_host = 'localhost'
            smtp_port = 25

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.sendmail(de, para, msg.as_string())

            return {
                'success': True,
                'message': 'Correo enviado exitosamente (modo local)',
                'destinatarios': para
            }

        elif modo == 'relay':
            # Modo relay: usar servidor SMTP externo
            smtp_host = smtp_host or os.getenv('SMTP_HOST')
            if not smtp_host:
                raise ValueError('Para modo relay, debe especificar smtp_host o configurar SMTP_HOST en .env')

            smtp_user = smtp_user or os.getenv('SMTP_USER')
            smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')

            # Configuración SSL/TLS
            if smtp_use_ssl is None:
                smtp_use_ssl = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'

            if smtp_use_tls is None:
                smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'

            # Puerto por defecto según SSL/TLS
            if smtp_port is None:
                smtp_port_env = os.getenv('SMTP_PORT')
                if smtp_port_env:
                    smtp_port = int(smtp_port_env)
                else:
                    smtp_port = 465 if smtp_use_ssl else 587

            # Conectar según configuración SSL
            if smtp_use_ssl:
                # SSL directo (puerto 465 típicamente)
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
            else:
                # Conexión normal con posible STARTTLS
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                if smtp_use_tls:
                    server.starttls()

            # Autenticar si hay credenciales
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)

            # Enviar
            server.sendmail(de, para, msg.as_string())
            server.quit()

            return {
                'success': True,
                'message': f'Correo enviado exitosamente (modo relay a {smtp_host})',
                'destinatarios': para
            }

        else:
            raise ValueError(f'Modo inválido: {modo}. Use "local" o "relay"')

    except smtplib.SMTPException as e:
        return {
            'success': False,
            'message': f'Error SMTP: {str(e)}',
            'destinatarios': para
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al enviar correo: {str(e)}',
            'destinatarios': para
        }


def validar_configuracion(modo: Optional[str] = None) -> dict:
    """
    Valida la configuración de email según el modo especificado.

    Args:
        modo: 'local' o 'relay' (opcional, usa EMAIL_MODE del .env)

    Returns:
        dict: {'valido': bool, 'mensaje': str, 'configuracion': dict}

    Example:
        >>> validacion = validar_configuracion()
        >>> if validacion['valido']:
        ...     print("Configuración OK")
        ... else:
        ...     print(f"Error: {validacion['mensaje']}")
    """
    modo = modo or os.getenv('EMAIL_MODE', 'local')

    config = {
        'modo': modo,
        'email_from': os.getenv('EMAIL_FROM'),
    }

    # Validar según modo
    if modo == 'local':
        # Modo local solo requiere EMAIL_FROM
        if not config['email_from']:
            return {
                'valido': False,
                'mensaje': 'Falta configurar EMAIL_FROM en .env',
                'configuracion': config
            }

        return {
            'valido': True,
            'mensaje': 'Configuración válida para modo local',
            'configuracion': config
        }

    elif modo == 'relay':
        # Modo relay requiere servidor SMTP
        config.update({
            'smtp_host': os.getenv('SMTP_HOST'),
            'smtp_port': os.getenv('SMTP_PORT'),
            'smtp_user': os.getenv('SMTP_USER'),
            'smtp_password': '***' if os.getenv('SMTP_PASSWORD') else None,
            'smtp_use_tls': os.getenv('SMTP_USE_TLS', 'true'),
            'smtp_use_ssl': os.getenv('SMTP_USE_SSL', 'false')
        })

        if not config['email_from']:
            return {
                'valido': False,
                'mensaje': 'Falta configurar EMAIL_FROM en .env',
                'configuracion': config
            }

        if not config['smtp_host']:
            return {
                'valido': False,
                'mensaje': 'Falta configurar SMTP_HOST en .env para modo relay',
                'configuracion': config
            }

        return {
            'valido': True,
            'mensaje': 'Configuración válida para modo relay',
            'configuracion': config
        }

    else:
        return {
            'valido': False,
            'mensaje': f'Modo inválido: {modo}. Use "local" o "relay"',
            'configuracion': config
        }
