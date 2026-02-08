# Integración de WhatsApp con Evolution API

Este documento muestra cómo integrar el módulo de WhatsApp en la aplicación FastAPI.

## Archivos del Paquete

1. **client.py** - Cliente Python para Evolution API
2. **router.py** - Router de FastAPI con endpoints para WhatsApp

## Integración en main.py

### Opción 1: Agregar router al app existente

```python
"""
API-MCP MSSQL SAPB1 - Punto de entrada principal.
"""
from auth_fastapi import create_auth_app
from paquetes.whatsapp import router as whatsapp_router  # <-- AGREGAR
import startup
import informacion

# Ejecutar verificaciones de inicio
startup.checks()

# Crear aplicación FastAPI con autenticación
app = create_auth_app(
    endpoint_prefix='/auth',
    database=None,
    public_prefix='',
    title="API-MCP MSSQL SAPB1",
    version="1.0.0"
)

# AGREGAR: Incluir router de WhatsApp
app.include_router(whatsapp_router)

if __name__ == '__main__':
    informacion.aplicacion()
```

### Opción 2: Uso directo sin router

Si prefieres usar el cliente directamente sin los endpoints:

```python
from paquetes.whatsapp import client

# En cualquier endpoint o función
async def mi_funcion():
    # Enviar mensaje
    result = client.send_text(
        instance_name="mi_whatsapp",
        number="5215512345678",
        text="Hola desde la aplicación"
    )
    return result
```

## Endpoints Disponibles

Una vez integrado, tendrás los siguientes endpoints:

### Gestión de Instancias

**Crear instancia:**
```bash
POST /whatsapp/instances
{
  "instance_name": "mi_whatsapp",
  "integration": "WHATSAPP-BAILEYS"
}
```

**Listar instancias:**
```bash
GET /whatsapp/instances
```

**Obtener QR Code:**
```bash
GET /whatsapp/qr/mi_whatsapp
```

**Verificar estado:**
```bash
GET /whatsapp/status/mi_whatsapp
```

**Eliminar instancia:**
```bash
DELETE /whatsapp/instances/mi_whatsapp
```

### Envío de Mensajes

**Enviar texto:**
```bash
POST /whatsapp/send-text
{
  "instance": "mi_whatsapp",
  "number": "5215512345678",
  "message": "Hola, este es un mensaje de prueba"
}
```

**Enviar imagen:**
```bash
POST /whatsapp/send-image
{
  "instance": "mi_whatsapp",
  "number": "5215512345678",
  "image_url": "https://ejemplo.com/imagen.jpg",
  "caption": "Mira esta imagen"
}
```

**Enviar documento:**
```bash
POST /whatsapp/send-document
{
  "instance": "mi_whatsapp",
  "number": "5215512345678",
  "document_url": "https://ejemplo.com/documento.pdf",
  "file_name": "reporte.pdf"
}
```

## Ejemplos de Uso

### 1. Desde curl (línea de comandos)

```bash
# Crear instancia
curl -X POST http://localhost:8000/whatsapp/instances \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "mi_whatsapp"
  }'

# Obtener QR para conectar
curl http://localhost:8000/whatsapp/qr/mi_whatsapp

# Enviar mensaje
curl -X POST http://localhost:8000/whatsapp/send-text \
  -H "Content-Type: application/json" \
  -d '{
    "instance": "mi_whatsapp",
    "number": "5215512345678",
    "message": "Hola desde curl!"
  }'
```

### 2. Desde Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Crear instancia
response = requests.post(
    f"{BASE_URL}/whatsapp/instances",
    json={"instance_name": "mi_whatsapp"}
)
print(response.json())

# Obtener QR
response = requests.get(f"{BASE_URL}/whatsapp/qr/mi_whatsapp")
qr_data = response.json()
print(f"QR Code: {qr_data['qr_code'][:50]}...")

# Enviar mensaje
response = requests.post(
    f"{BASE_URL}/whatsapp/send-text",
    json={
        "instance": "mi_whatsapp",
        "number": "5215512345678",
        "message": "Hola desde Python!"
    }
)
print(response.json())
```

### 3. Desde JavaScript (fetch)

```javascript
// Enviar mensaje
async function enviarMensaje() {
  const response = await fetch('http://localhost:8000/whatsapp/send-text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      instance: 'mi_whatsapp',
      number: '5215512345678',
      message: 'Hola desde JavaScript!'
    })
  });

  const data = await response.json();
  console.log(data);
}

enviarMensaje();
```

### 4. Uso interno en endpoints FastAPI

```python
from fastapi import APIRouter
from paquetes.whatsapp import client

router = APIRouter()

@router.post("/enviar-notificacion")
async def enviar_notificacion(usuario_id: int, mensaje: str):
    # Obtener número del usuario desde BD
    numero = obtener_numero_usuario(usuario_id)

    # Enviar mensaje de WhatsApp
    resultado = client.send_text(
        instance_name="mi_whatsapp",
        number=numero,
        text=mensaje
    )

    return {
        "success": True,
        "message": "Notificación enviada",
        "whatsapp_response": resultado
    }
```

## Configuración en .env

Agregar a `/infraestructura/.env.api-mcp`:

```bash
# Evolution API
EVOLUTION_API_URL=http://evolution-api-mcp:8080
EVOLUTION_API_KEY=6bb1d618b347017b9bd94160a7774ade6a91ad22f47069ee0914b4a27c4348b0
```

## Documentación Interactiva

Una vez integrado, la documentación estará disponible en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Busca la sección "WhatsApp" para ver todos los endpoints disponibles.

## Flujo Completo de Trabajo

### Paso 1: Crear y Conectar Instancia

```bash
# 1. Crear instancia
curl -X POST http://localhost:8000/whatsapp/instances \
  -H "Content-Type: application/json" \
  -d '{"instance_name": "mi_whatsapp"}'

# 2. Obtener QR code
curl http://localhost:8000/whatsapp/qr/mi_whatsapp

# 3. Escanear QR con WhatsApp móvil

# 4. Verificar conexión
curl http://localhost:8000/whatsapp/status/mi_whatsapp
# Debe retornar: "state": "open"
```

### Paso 2: Enviar Mensajes

```bash
# Enviar mensaje de texto
curl -X POST http://localhost:8000/whatsapp/send-text \
  -H "Content-Type: application/json" \
  -d '{
    "instance": "mi_whatsapp",
    "number": "5215512345678",
    "message": "Hola, este es un mensaje de prueba"
  }'
```

## Casos de Uso Comunes

### 1. Notificaciones Automáticas

```python
from paquetes.whatsapp import client

async def notificar_pedido_nuevo(pedido_id: int):
    """Notifica al cliente cuando se crea un pedido nuevo."""
    pedido = obtener_pedido(pedido_id)

    mensaje = f"""
    ¡Pedido #{pedido.id} confirmado! ✅

    Total: ${pedido.total}
    Entrega estimada: {pedido.fecha_entrega}

    Gracias por tu compra.
    """

    client.send_text(
        instance_name="ventas",
        number=pedido.cliente_telefono,
        text=mensaje
    )
```

### 2. Recordatorios

```python
from paquetes.whatsapp import client

async def enviar_recordatorio_cita(cita_id: int):
    """Envía recordatorio de cita 24h antes."""
    cita = obtener_cita(cita_id)

    mensaje = f"""
    Recordatorio de Cita 📅

    Fecha: {cita.fecha}
    Hora: {cita.hora}
    Lugar: {cita.lugar}

    Te esperamos!
    """

    client.send_text(
        instance_name="citas",
        number=cita.paciente_telefono,
        text=mensaje
    )
```

### 3. Alertas Administrativas

```python
from paquetes.whatsapp import client

async def alertar_stock_bajo(producto_id: int):
    """Alerta al admin cuando un producto tiene stock bajo."""
    producto = obtener_producto(producto_id)

    mensaje = f"""
    ⚠️ ALERTA DE STOCK BAJO

    Producto: {producto.nombre}
    Stock actual: {producto.stock}
    Stock mínimo: {producto.stock_minimo}

    Reabastecer pronto.
    """

    client.send_text(
        instance_name="admin",
        number="5215512345678",  # Número del admin
        text=mensaje
    )
```

## Troubleshooting

### Error: "Instance not connected"

La instancia no está conectada. Soluci ones:

1. Obtener nuevo QR: `GET /whatsapp/qr/{instance}`
2. Escanear con WhatsApp móvil
3. Verificar estado: `GET /whatsapp/status/{instance}`

### Error: "Request timeout"

Evolution API puede estar detenido. Verificar:

```bash
docker ps | grep evolution-api-mcp
docker logs evolution-api-mcp --tail 50
```

### Mensaje no se envía

1. Verificar que la instancia esté conectada
2. Verificar formato del número (debe incluir código de país)
3. Verificar que el número existe en WhatsApp

## Referencias

- [Documentación Evolution API](https://doc.evolution-api.com/v2/)
- [Guía Evolution API](../../../../infraestructura/EVOLUTION_API_GUIA.md)
- [Código Cliente](./client.py)
- [Router FastAPI](./router.py)
