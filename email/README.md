# Módulo Email

Módulo genérico y portable para envío de correos electrónicos con soporte para postfix local y relay SMTP externo.

## 📋 Contenido

- [Descripción](#descripción)
- [Características](#características)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Funciones Disponibles](#funciones-disponibles)
- [Ejemplos](#ejemplos)
- [Solución de Problemas](#solución-de-problemas)

---

## Descripción

El módulo `email` proporciona funcionalidades para envío de correos electrónicos con dos modos de operación:

- **Modo local**: Envío directo usando postfix instalado localmente (localhost:25)
- **Modo relay**: Envío mediante servidor SMTP externo con autenticación (Gmail, Outlook, servidor corporativo, etc.)

### Características

✓ **Genérico y portable**: No depende de configuración específica del proyecto
✓ **Flexible**: Soporta configuración por parámetros o variables de entorno
✓ **Múltiples destinatarios**: Envío a uno o varios destinatarios simultáneamente
✓ **Adjuntos**: Soporte para archivos adjuntos múltiples
✓ **HTML por defecto**: Correos en formato HTML (default) o texto plano
✓ **Dominio automático**: Agrega `@smtp.local` si el remitente no tiene dominio
✓ **Dos modos**: Postfix local o relay SMTP externo
✓ **Seguro**: Soporte para TLS/SSL

---

## Instalación

### Dependencias Python

El módulo usa solo librerías estándar de Python (no requiere instalación adicional):
- `smtplib`: Protocolo SMTP
- `email`: Construcción de mensajes MIME

### Servicio Postfix (para modo local)

Si usas modo local, necesitas el servicio postfix corriendo:

```bash
# Verificar que postfix está corriendo
docker exec api-mcp service postfix status

# Iniciar postfix si no está corriendo
docker exec api-mcp service postfix start
```

**Configuración de Postfix:**

El servidor postfix está configurado con:
```
myhostname = postfix
mydomain = smtp.local
inet_interfaces = all
```

Esto permite que los correos se envíen desde el dominio `smtp.local`.

---

## Configuración

### Variables de Entorno

Configurar en `/infraestructura/.env`:

```bash
# ============================================================================
# CONFIGURACIÓN DE EMAIL
# ============================================================================

# Modo de envío: 'local' (postfix) o 'relay' (SMTP externo)
EMAIL_MODE=local

# Email del remitente por defecto (opcional)
# Si no tiene dominio (@), se agrega @smtp.local automáticamente
EMAIL_FROM=sistema

# --- Configuración para modo RELAY (SMTP externo) ---

# Servidor SMTP (Gmail, Outlook, servidor corporativo, etc.)
SMTP_HOST=smtp.gmail.com

# Puerto SMTP (587 para TLS, 465 para SSL, 25 para no cifrado)
SMTP_PORT=587

# Credenciales SMTP
SMTP_USER=mi_cuenta@gmail.com
SMTP_PASSWORD=mi_password_o_app_password

# Seguridad
SMTP_USE_TLS=true   # STARTTLS (puerto 587)
SMTP_USE_SSL=false  # SSL directo (puerto 465)
```

### Configuración por Servidor

#### Gmail

```bash
EMAIL_MODE=relay
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_cuenta@gmail.com
SMTP_PASSWORD=tu_app_password  # Generar en: https://myaccount.google.com/apppasswords
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

#### Outlook/Office 365

```bash
EMAIL_MODE=relay
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=tu_cuenta@outlook.com
SMTP_PASSWORD=tu_password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

#### Servidor Corporativo

```bash
EMAIL_MODE=relay
SMTP_HOST=smtp.empresa.com
SMTP_PORT=25
SMTP_USER=usuario@empresa.com
SMTP_PASSWORD=password
SMTP_USE_TLS=false
SMTP_USE_SSL=false
```

#### Modo Local (Postfix)

```bash
EMAIL_MODE=local
EMAIL_FROM=sistema  # Se convierte en sistema@smtp.local
# No requiere configuración SMTP adicional
```

---

## Uso

### Importar el Módulo

```python
from paquetes.email import send_email, validar_configuracion
```

---

## Funciones Disponibles

### `send_email()`

Envía un correo electrónico con soporte para múltiples destinatarios y adjuntos.

```python
send_email(
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
) -> dict
```

**Parámetros:**

| Parámetro | Tipo | Descripción | Requerido |
|-----------|------|-------------|-----------|
| `para` | `str` o `list` | Destinatario(s) del correo | Sí |
| `titulo` | `str` | Asunto del correo | Sí |
| `cuerpo` | `str` | Contenido del mensaje | No |
| `de` | `str` | Remitente (usa `EMAIL_FROM` si no se especifica, agrega `@smtp.local` si no tiene dominio) | No |
| `adjuntos` | `list` | Lista de rutas de archivos a adjuntar | No |
| `html` | `bool` | Si True, interpreta cuerpo como HTML; si False, texto plano (default: `True`) | No |
| `modo` | `str` | `'local'` o `'relay'` (usa `EMAIL_MODE` si no se especifica) | No |
| `smtp_host` | `str` | Servidor SMTP (solo para relay) | No* |
| `smtp_port` | `int` | Puerto SMTP | No |
| `smtp_user` | `str` | Usuario SMTP | No |
| `smtp_password` | `str` | Contraseña SMTP | No |
| `smtp_use_tls` | `bool` | Usar STARTTLS | No |
| `smtp_use_ssl` | `bool` | Usar SSL directo | No |

\* Requerido para modo relay si no está en `.env`

**Retorna:**

```python
{
    'success': bool,           # True si se envió correctamente
    'message': str,            # Mensaje descriptivo
    'destinatarios': list      # Lista de destinatarios
}
```

---

### `validar_configuracion()`

Valida la configuración de email según el modo especificado.

```python
validar_configuracion(
    modo: Optional[str] = None
) -> dict
```

**Retorna:**

```python
{
    'valido': bool,            # True si la configuración es válida
    'mensaje': str,            # Mensaje descriptivo
    'configuracion': dict      # Configuración actual
}
```

---

## Ejemplos

### Ejemplo 1: Envío Simple (Modo Local)

```python
from paquetes.email import send_email

# Envío básico con postfix local (HTML por defecto)
result = send_email(
    para='usuario@ejemplo.com',
    titulo='Prueba de correo',
    cuerpo='<p>Este es un mensaje de prueba en <strong>HTML</strong>.</p>',
    de='sistema'  # Se convierte en sistema@smtp.local automáticamente
)

if result['success']:
    print(f"Correo enviado a {result['destinatarios']}")
else:
    print(f"Error: {result['message']}")
```

### Ejemplo 2: Envío en Texto Plano

```python
# Para enviar en texto plano, especificar html=False
result = send_email(
    para='usuario@ejemplo.com',
    titulo='Prueba texto plano',
    cuerpo='Este es un mensaje de prueba en texto plano.',
    html=False,  # Explícitamente texto plano
    de='avisos'  # Se convierte en avisos@smtp.local
)
```

### Ejemplo 3: Múltiples Destinatarios

```python
# Enviar a varios destinatarios
result = send_email(
    para=['usuario1@ejemplo.com', 'usuario2@ejemplo.com', 'usuario3@ejemplo.com'],
    titulo='Notificación Masiva',
    cuerpo='<h1>Mensaje para todos</h1><p>Este es un mensaje importante.</p>',
    de='notificaciones'
)
```

### Ejemplo 4: Correo HTML Elaborado

```python
# Enviar correo en formato HTML (por defecto, no es necesario especificar html=True)
html_content = """
<html>
  <head>
    <style>
      body { font-family: Arial, sans-serif; }
      h1 { color: #333; }
      .destacado { background-color: #f0f0f0; padding: 10px; }
    </style>
  </head>
  <body>
    <h1>Bienvenido</h1>
    <p>Este es un correo con <strong>formato HTML</strong>.</p>
    <div class="destacado">
      <ul>
        <li>Punto 1</li>
        <li>Punto 2</li>
      </ul>
    </div>
  </body>
</html>
"""

result = send_email(
    para='cliente@ejemplo.com',
    titulo='Bienvenida',
    cuerpo=html_content,
    de='ventas'  # Se convierte en ventas@smtp.local
)
```

### Ejemplo 5: Con Adjuntos

```python
# Enviar correo con archivos adjuntos
result = send_email(
    para='cliente@ejemplo.com',
    titulo='Documentos adjuntos',
    cuerpo='<p>Adjunto encontrará los documentos solicitados.</p>',
    adjuntos=[
        '/ruta/a/factura_enero.pdf',
        '/ruta/a/recibo.pdf'
    ],
    de='contabilidad'
)
```

### Ejemplo 6: Modo Relay con Gmail

```python
# Envío mediante Gmail (requiere App Password)
result = send_email(
    para='destinatario@ejemplo.com',
    titulo='Notificación',
    cuerpo='<p>Mensaje enviado vía <strong>Gmail</strong></p>',
    modo='relay',
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    smtp_user='mi_cuenta@gmail.com',
    smtp_password='xxxx xxxx xxxx xxxx',  # App Password de Gmail
    smtp_use_tls=True,
    de='mi_cuenta@gmail.com'
)
```

### Ejemplo 7: Usar Variables de Entorno

```python
# Configurar en .env:
# EMAIL_MODE=local
# EMAIL_FROM=sistema

# Envío usando configuración del .env
result = send_email(
    para='usuario@ejemplo.com',
    titulo='Mensaje automático',
    cuerpo='<p>Usando configuración de .env</p>'
)
# No es necesario especificar modo ni remitente
# Remitente será: sistema@smtp.local (dominio agregado automáticamente)
```

### Ejemplo 8: Validar Configuración

```python
from paquetes.email import validar_configuracion

# Verificar configuración antes de enviar
validacion = validar_configuracion()

if validacion['valido']:
    print("✓ Configuración válida")
    print(f"  Modo: {validacion['configuracion']['modo']}")
    print(f"  From: {validacion['configuracion']['email_from']}")
else:
    print(f"✗ Error en configuración: {validacion['mensaje']}")
```

### Ejemplo 9: Integración con API

```python
from fastapi import FastAPI, HTTPException
from paquetes.email import send_email
from pydantic import BaseModel

app = FastAPI()

class EmailRequest(BaseModel):
    destinatarios: list
    asunto: str
    mensaje: str

@app.post("/enviar-notificacion")
async def enviar_notificacion(email: EmailRequest):
    """Endpoint para enviar notificaciones por email."""
    result = send_email(
        para=email.destinatarios,
        titulo=email.asunto,
        cuerpo=email.mensaje,
        de='api'  # Se convierte en api@smtp.local
    )

    if result['success']:
        return {"mensaje": "Correo enviado exitosamente"}
    else:
        raise HTTPException(status_code=500, detail=result['message'])
```

---

## Solución de Problemas

### Error: "Connection refused" (Modo Local)

**Causa**: Postfix no está corriendo en el contenedor.

**Solución**:

```bash
# Iniciar postfix
docker exec api-mcp service postfix start

# Verificar estado
docker exec api-mcp service postfix status
```

### Error: "Authentication failed" (Modo Relay)

**Causa**: Credenciales SMTP incorrectas o no configuradas.

**Solución**:

- Verificar `SMTP_USER` y `SMTP_PASSWORD` en `.env`
- Para Gmail, usar App Password en lugar de contraseña regular
- Verificar que la cuenta permita acceso SMTP

### Error: "Archivo no encontrado" (Adjuntos)

**Causa**: La ruta del adjunto no existe.

**Solución**:

```python
import os

# Verificar que el archivo existe antes de enviarlo
archivo = '/ruta/a/archivo.pdf'
if os.path.exists(archivo):
    result = send_email(
        para='usuario@ejemplo.com',
        titulo='Con adjunto',
        adjuntos=[archivo]
    )
```

### Error: "SMTP server doesn't support TLS"

**Causa**: El servidor SMTP no soporta TLS pero `SMTP_USE_TLS=true`.

**Solución**:

```bash
# En .env, cambiar a:
SMTP_USE_TLS=false
```

### Correos No Llegan (Modo Local)

**Causa**: Los correos enviados desde `@smtp.local` pueden ser rechazados por servidores externos que validan dominios (SPF, DKIM, DNS).

**Solución**:

**Opción 1: Usar modo relay con servidor SMTP válido (Recomendado)**
```bash
EMAIL_MODE=relay
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_cuenta@gmail.com
SMTP_PASSWORD=app_password
SMTP_USE_TLS=true
```

**Opción 2: Configurar un dominio válido**
- Cambiar `mydomain` en postfix a un dominio real que controles
- Configurar registros DNS, SPF y DKIM para ese dominio

### Error: "El parámetro 'de' es requerido"

**Causa**: No se especificó remitente y `EMAIL_FROM` no está configurado.

**Solución**:

```bash
# Opción 1: Configurar en .env
EMAIL_FROM=sistema

# Opción 2: Especificar en cada llamada
result = send_email(
    para='usuario@ejemplo.com',
    titulo='Prueba',
    de='remitente'  # Se convierte en remitente@smtp.local
)
```

---

## Configuración de Gmail (App Passwords)

Para usar Gmail como servidor SMTP, necesitas generar una App Password:

1. Ir a https://myaccount.google.com/apppasswords
2. Seleccionar "Correo" y "Otro" como dispositivo
3. Generar la contraseña
4. Usar esa contraseña en `SMTP_PASSWORD`

**Configuración .env para Gmail:**

```bash
EMAIL_MODE=relay
EMAIL_FROM=tu_cuenta@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_cuenta@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

---

## Buenas Prácticas

### 1. Usar Variables de Entorno en Producción

```bash
# .env
EMAIL_MODE=relay
EMAIL_FROM=${SISTEMA_EMAIL}
SMTP_PASSWORD=${SMTP_SECRET}
```

### 2. Validar Antes de Enviar

```python
# Verificar configuración al inicio de la aplicación
from paquetes.email import validar_configuracion

validacion = validar_configuracion()
if not validacion['valido']:
    print(f"ADVERTENCIA: {validacion['mensaje']}")
```

### 3. Manejo de Errores

```python
result = send_email(
    para='usuario@ejemplo.com',
    titulo='Notificación',
    cuerpo='Contenido'
)

if not result['success']:
    # Registrar error, reintentar, notificar, etc.
    print(f"Error al enviar correo: {result['message']}")
```

### 4. Templates HTML

```python
# Usar templates para correos HTML consistentes
def generar_email_bienvenida(nombre_usuario):
    html = f"""
    <html>
      <body>
        <h1>Bienvenido {nombre_usuario}</h1>
        <p>Gracias por registrarte...</p>
      </body>
    </html>
    """
    return html

# Enviar
result = send_email(
    para='nuevo@usuario.com',
    titulo='Bienvenida',
    cuerpo=generar_email_bienvenida('Juan Pérez'),
    de='sistema'
)
```

### 5. Dominio Automático

El módulo agrega automáticamente `@smtp.local` si el remitente no tiene dominio:

```python
# Estos son equivalentes en modo local:
send_email(..., de='sistema')           # → sistema@smtp.local
send_email(..., de='sistema@smtp.local') # → sistema@smtp.local

# Para usar un dominio específico:
send_email(..., de='noreply@miempresa.com')  # → noreply@miempresa.com
```

---

## Portabilidad

Este módulo es completamente portable:

```python
# Opción 1: Copiar módulo a otro proyecto
cp -r paquetes/email /otro/proyecto/paquetes/

# Opción 2: Usar directamente
from paquetes.email import send_email
```

**No requiere**:
- Archivos de configuración específicos
- Estructura de proyecto particular
- Dependencias externas (solo librerías estándar)

---

**Versión:** 1.0.1
**Última actualización:** 2026-01-31
**Configuración Postfix:** `myhostname=postfix`, `mydomain=smtp.local`
**Formato por defecto:** HTML (`html=True`)
**Dominio por defecto:** `@smtp.local` (agregado automáticamente si no se especifica)
