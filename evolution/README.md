# Módulo Evolution API

Cliente genérico y portable para [Evolution API](https://doc.evolution-api.com/v2/) - Sistema multi-instancia de WhatsApp.

> ⚠️ **MÓDULO GENÉRICO**: Este módulo NO tiene valores por defecto hardcodeados. El usuario debe proporcionar TODAS las variables de conexión en el archivo `.env`. Ver [configuración](#-configuración) para más detalles.

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso Rápido](#-uso-rápido)
- [API Completa](#-api-completa)
- [Ejemplos](#-ejemplos)

---

## 📦 Descripción

Evolution API es una solución multi-instancia para WhatsApp que permite gestionar múltiples números de WhatsApp desde una sola API.

Este módulo proporciona un cliente Python genérico para:
- ✅ **Listar instancias** configuradas
- ✅ **Crear nuevas instancias** de WhatsApp
- ✅ **Eliminar instancias** existentes
- ✅ **Enviar mensajes** de texto, imágenes y documentos
- ✅ **Verificar estado** de conexión
- ✅ **Obtener QR codes** para vinculación

**Total de funciones:** 14 funciones

---

## 🔧 Instalación

### Requisitos

```bash
pip install requests
```

### Importación

```python
# Opción 1: Importar el cliente
from evolution import EvolutionClient

# Opción 2: Función de conveniencia
from evolution import get_evolution_client
```

---

## ⚙️ Configuración

### Variables de Entorno

⚠️ **El módulo es completamente genérico y NO tiene valores por defecto**.

Configura las siguientes variables en `.env`:

```env
# Evolution API (REQUERIDO)
EVOLUTION_API_URL=http://evolution-api-mcp:8080
EVOLUTION_API_KEY=tu_api_key_aqui
```

**Generar API Key segura:**
```bash
openssl rand -hex 32
```

### Uso sin Variables de Entorno

También puedes pasar las credenciales directamente:

```python
from evolution import EvolutionClient

client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="tu_api_key"
)
```

---

## 🚀 Uso Rápido

### 1. Crear Cliente

```python
from evolution import get_evolution_client

# Lee configuración de .env
client = get_evolution_client()

# O con parámetros directos
client = get_evolution_client(
    base_url="http://localhost:8080",
    api_key="tu_api_key"
)
```

### 2. Listar Instancias

```python
# Obtener todas las instancias
instances = client.list_instances()

for inst in instances:
    print(f"{inst['instanceName']}: {inst['connectionStatus']}")
```

### 3. Crear Nueva Instancia

```python
# Crear instancia y obtener QR code
result = client.create_instance("mi_whatsapp")

print("Escanea este QR con WhatsApp móvil:")
print(result['qrcode']['code'])
```

### 4. Enviar Mensaje

```python
# Enviar mensaje de texto
result = client.send_text(
    instance_name="mi_whatsapp",
    number="5215512345678",
    text="¡Hola desde Evolution API!"
)

print(f"Mensaje enviado. ID: {result['key']['id']}")
```

### 5. Verificar Conexión

```python
if client.is_instance_connected("mi_whatsapp"):
    print("✓ WhatsApp conectado y listo")
else:
    print("✗ WhatsApp no conectado")
```

---

## 📚 API Completa

### Gestión de Instancias (7 funciones)

#### `list_instances()`
Lista todas las instancias configuradas.

```python
instances = client.list_instances()
# Retorna: [{'instanceName': 'mi_wa', 'connectionStatus': 'open', ...}, ...]
```

#### `create_instance(instance_name, qrcode=True, ...)`
Crea una nueva instancia de WhatsApp.

```python
result = client.create_instance("mi_whatsapp")
# Retorna: {'qrcode': {'code': '...', 'base64': '...'}, ...}
```

**Parámetros:**
- `instance_name` (str): Nombre único para la instancia
- `qrcode` (bool): Generar QR code (default: True)
- `integration` (str): Tipo de integración (default: "WHATSAPP-BAILEYS")
- `webhook_url` (str, opcional): URL para webhooks
- `webhook_events` (list, opcional): Eventos que disparan webhook

#### `delete_instance(instance_name)`
Elimina una instancia.

```python
result = client.delete_instance("mi_whatsapp")
# Retorna: {'message': 'Instance deleted successfully'}
```

#### `get_instance_info(instance_name)`
Obtiene información detallada de una instancia.

```python
info = client.get_instance_info("mi_whatsapp")
# Retorna: {'connectionStatus': 'open', 'state': 'open', ...}
```

#### `get_qr_code(instance_name)`
Obtiene el código QR para vincular la instancia.

```python
qr = client.get_qr_code("mi_whatsapp")
print(qr['code'])  # Código QR en texto
```

#### `logout_instance(instance_name)`
Desconecta una instancia (cierra sesión).

```python
result = client.logout_instance("mi_whatsapp")
```

#### `restart_instance(instance_name)`
Reinicia una instancia.

```python
result = client.restart_instance("mi_whatsapp")
```

---

### Envío de Mensajes (4 funciones)

#### `send_text(instance_name, number, text)`
Envía un mensaje de texto.

```python
result = client.send_text(
    instance_name="mi_whatsapp",
    number="5215512345678",
    text="Hola, este es un mensaje de prueba"
)
```

**Formato de número:** Código país + número (ej: 5215512345678 para México)

#### `send_media(instance_name, number, media_url, media_type, ...)`
Envía un archivo multimedia.

```python
result = client.send_media(
    instance_name="mi_whatsapp",
    number="5215512345678",
    media_url="https://ejemplo.com/archivo.jpg",
    media_type="image",  # image, video, audio, document
    caption="Mira esta imagen"
)
```

#### `send_image(instance_name, number, image_url, caption=None)`
Envía una imagen (atajo para `send_media`).

```python
result = client.send_image(
    instance_name="mi_whatsapp",
    number="5215512345678",
    image_url="https://ejemplo.com/foto.jpg",
    caption="Nueva foto"
)
```

#### `send_document(instance_name, number, document_url, filename, caption=None)`
Envía un documento (atajo para `send_media`).

```python
result = client.send_document(
    instance_name="mi_whatsapp",
    number="5215512345678",
    document_url="https://ejemplo.com/reporte.pdf",
    filename="Reporte_Mensual.pdf"
)
```

---

### Utilidades (3 funciones)

#### `is_instance_connected(instance_name)`
Verifica si una instancia está conectada.

```python
connected = client.is_instance_connected("mi_whatsapp")
# Retorna: True o False
```

#### `get_instance_status(instance_name)`
Obtiene el estado de conexión.

```python
status = client.get_instance_status("mi_whatsapp")
# Retorna: 'open', 'close', 'connecting', etc.
```

#### `_format_phone_number(phone, country_code='52')`
Formatea un número de teléfono al formato de WhatsApp.

```python
formatted = client._format_phone_number("5512345678")
# Retorna: "5215512345678"
```

---

## 💡 Ejemplos

### Ejemplo 1: Configurar y Enviar Mensaje

```python
from evolution import get_evolution_client

# Crear cliente
client = get_evolution_client()

# Verificar si hay instancias
instances = client.list_instances()

if not instances:
    # Crear primera instancia
    print("Creando instancia...")
    result = client.create_instance("ventas")
    print("Escanea este QR code:")
    print(result['qrcode']['code'])
else:
    # Usar instancia existente
    instance = instances[0]['instanceName']

    if client.is_instance_connected(instance):
        # Enviar mensaje
        client.send_text(
            instance_name=instance,
            number="5215512345678",
            text="¡Mensaje desde Python!"
        )
        print("✓ Mensaje enviado")
    else:
        print("✗ Instancia no conectada")
```

### Ejemplo 2: Gestión Completa de Instancias

```python
from evolution import EvolutionClient

client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="tu_api_key"
)

# Crear múltiples instancias
departamentos = ["ventas", "soporte", "marketing"]

for dept in departamentos:
    try:
        result = client.create_instance(dept)
        print(f"✓ Instancia '{dept}' creada")
        print(f"  QR: {result['qrcode']['code'][:50]}...")
    except Exception as e:
        print(f"✗ Error al crear '{dept}': {e}")

# Listar todas
print("\n=== Instancias Activas ===")
for inst in client.list_instances():
    status = "🟢 Conectada" if inst.get('connectionStatus') == 'open' else "🔴 Desconectada"
    print(f"{inst['instanceName']}: {status}")
```

### Ejemplo 3: Envío Masivo con Verificación

```python
from evolution import get_evolution_client

client = get_evolution_client()
instance = "mi_whatsapp"

# Verificar conexión antes de enviar
if not client.is_instance_connected(instance):
    print("Error: WhatsApp no conectado")
    exit(1)

# Lista de destinatarios
contactos = [
    {"numero": "5215512345678", "nombre": "Juan"},
    {"numero": "5215587654321", "nombre": "María"},
]

# Enviar a todos
for contacto in contactos:
    try:
        result = client.send_text(
            instance_name=instance,
            number=contacto["numero"],
            text=f"Hola {contacto['nombre']}, este es un mensaje personalizado"
        )
        print(f"✓ Enviado a {contacto['nombre']}")
    except Exception as e:
        print(f"✗ Error al enviar a {contacto['nombre']}: {e}")
```

### Ejemplo 4: Enviar Imagen con Documento

```python
from evolution import get_evolution_client

client = get_evolution_client()

# Enviar imagen
client.send_image(
    instance_name="ventas",
    number="5215512345678",
    image_url="https://ejemplo.com/productos/nuevo.jpg",
    caption="¡Nuevo producto disponible!"
)

# Enviar documento
client.send_document(
    instance_name="ventas",
    number="5215512345678",
    document_url="https://ejemplo.com/catalogo.pdf",
    filename="Catalogo_2026.pdf",
    caption="Adjunto nuestro catálogo actualizado"
)
```

---

## 🔐 Seguridad

### Mejores Prácticas

1. **Nunca hardcodear API Keys** en el código
2. **Usar variables de entorno** para credenciales
3. **Generar API Keys seguras** con `openssl rand -hex 32`
4. **Rotar API Keys periódicamente**
5. **Limitar acceso** a la Evolution API solo desde IPs autorizadas

### Ejemplo con .env

```bash
# .env
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=6bb1d618b347017b9bd94160a7774ade6a91ad22f47069ee0914b4a27c4348b0
```

```python
# app.py
from evolution import get_evolution_client

# Lee automáticamente de .env
client = get_evolution_client()
```

---

## 🌐 Integración con FastAPI

```python
from fastapi import FastAPI, HTTPException
from evolution import get_evolution_client
from pydantic import BaseModel

app = FastAPI()
evo_client = get_evolution_client()

class MensajeRequest(BaseModel):
    instance: str
    numero: str
    texto: str

@app.post("/whatsapp/enviar")
async def enviar_mensaje(msg: MensajeRequest):
    try:
        result = evo_client.send_text(
            instance_name=msg.instance,
            number=msg.numero,
            text=msg.texto
        )
        return {"success": True, "message_id": result['key']['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/whatsapp/instancias")
async def listar_instancias():
    return evo_client.list_instances()
```

---

## 📖 Documentación Relacionada

- **[Evolution API Oficial](https://doc.evolution-api.com/v2/)** - Documentación completa de la API
- **[Configuración de Infraestructura](../../../infraestructura/README.md)** - Setup de Evolution API con Docker
- **[Paquete WhatsApp](../whatsapp/README.md)** - Wrapper de alto nivel para WhatsApp

---

## 🆘 Solución de Problemas

### Error: "Evolution API URL no configurada"

**Causa:** No se configuró `EVOLUTION_API_URL` en `.env`

**Solución:**
```bash
# Agregar a .env
EVOLUTION_API_URL=http://evolution-api-mcp:8080
```

### Error: "Evolution API Key no configurada"

**Causa:** No se configuró `EVOLUTION_API_KEY` en `.env`

**Solución:**
```bash
# Generar y agregar a .env
openssl rand -hex 32
# Copiar output y agregarlo a .env
EVOLUTION_API_KEY=<output_del_comando>
```

### Error: Connection refused

**Causa:** Evolution API no está corriendo

**Solución:**
```bash
# Verificar que el servicio esté corriendo
docker ps | grep evolution

# Levantar si es necesario
cd infraestructura
docker compose up -d evolution-api-mcp
```

### Instancia no conecta

**Causa:** QR code no fue escaneado o expiró

**Solución:**
```python
# Obtener nuevo QR code
qr = client.get_qr_code("mi_whatsapp")
print(qr['code'])
# Escanear con WhatsApp móvil
```

---

## 📋 Referencia Rápida

| Función | Descripción | Ejemplo |
|---------|-------------|---------|
| `list_instances()` | Lista instancias | `client.list_instances()` |
| `create_instance(name)` | Crea instancia | `client.create_instance("ventas")` |
| `delete_instance(name)` | Elimina instancia | `client.delete_instance("ventas")` |
| `send_text(inst, num, txt)` | Envía texto | `client.send_text("ventas", "521...", "Hola")` |
| `send_image(inst, num, url)` | Envía imagen | `client.send_image("ventas", "521...", "http://...")` |
| `is_instance_connected(name)` | Verifica conexión | `client.is_instance_connected("ventas")` |

---

**Versión:** 1.0.0
**Última actualización:** 2026-01-31
**Funciones totales:** 14 funciones
**Documentación oficial:** https://doc.evolution-api.com/v2/
