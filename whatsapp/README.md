# Paquete WhatsApp - Evolution API

Integración completa de WhatsApp usando Evolution API para envío de mensajes desde FastAPI.

> **MÓDULO GENÉRICO Y PORTABLE**: Este paquete NO tiene valores hardcodeados. Es un **wrapper** sobre el módulo [evolution](../evolution/README.md) que extiende `EvolutionClient` con funcionalidad adicional (webhooks) y proporciona un router FastAPI completo.
>
> ⚠️ **Configuración requerida**: Debes proporcionar `EVOLUTION_API_URL` y `EVOLUTION_API_KEY` en `.env` o configurar el cliente explícitamente.

## Estructura del Paquete

```
paquetes/whatsapp/
├── __init__.py              # Exporta componentes
├── client.py                # Wrapper genérico sobre evolution.EvolutionClient
├── router.py                # Router FastAPI con endpoints REST
├── README.md                # Este archivo
└── INTEGRATION_EXAMPLES.md  # Guía de integración con ejemplos
```

**Tests:** Ver [test_whatsapp.py](../tests/whatsapp/test_whatsapp.py) en `paquetes/tests/whatsapp/`

## Archivos del Paquete

| Archivo | Descripción |
|---------|-------------|
| [\_\_init\_\_.py](__init__.py) | Exporta EvolutionAPIClient, MessageType, router, set_evolution_client |
| [client.py](client.py) | Wrapper genérico sobre evolution.EvolutionClient (3KB) |
| [router.py](router.py) | Router FastAPI con endpoints REST (13KB) |
| [README.md](README.md) | Esta documentación |
| [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md) | Guía de integración completa |

## Instalación

La librería `requests` es requerida:

```bash
docker exec api-mcp pip3 install requests
```

## Inicio Rápido

### 1. Configurar Variables de Entorno

En `.env.api-mcp`:

```bash
# Evolution API (REQUERIDO)
EVOLUTION_API_URL=http://evolution-api-mcp:8080
EVOLUTION_API_KEY=tu_api_key_aqui
```

**Generar API Key segura:**
```bash
openssl rand -hex 32
```

### 2. Integrar en FastAPI

Editar `main.py` y agregar:

```python
from paquetes.whatsapp import router, set_evolution_client
from paquetes.evolution import EvolutionClient

# Configurar cliente (lee de .env)
client = EvolutionClient()
set_evolution_client(client)

# Agregar router de WhatsApp
app.include_router(router)
```

### 3. Crear y Conectar Instancia

```bash
# Crear instancia
curl -X POST http://localhost:8000/whatsapp/instances \
  -H "Content-Type: application/json" \
  -d '{"instance_name": "mi_whatsapp"}'

# Obtener QR code
curl http://localhost:8000/whatsapp/qr/mi_whatsapp

# Escanear el QR con WhatsApp móvil
```

### 4. Enviar Mensaje

```bash
curl -X POST http://localhost:8000/whatsapp/send-text \
  -H "Content-Type: application/json" \
  -d '{
    "instance": "mi_whatsapp",
    "number": "5215512345678",
    "message": "Hola desde Evolution API!"
  }'
```

## Uso Directo (sin endpoints)

```python
from paquetes.evolution import EvolutionClient

# Crear cliente (lee de .env)
client = EvolutionClient()

# O con parámetros explícitos
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="tu_api_key"
)

# Enviar mensaje
result = client.send_text(
    instance_name="mi_whatsapp",
    number="5215512345678",
    text="Hola, mensaje de prueba"
)

# Enviar imagen
result = client.send_image(
    instance_name="mi_whatsapp",
    number="5215512345678",
    image_url="https://ejemplo.com/imagen.jpg",
    caption="Mira esta imagen"
)

# Verificar si está conectado
if client.is_instance_connected("mi_whatsapp"):
    print("WhatsApp conectado y listo")
```

## Endpoints Disponibles

Una vez integrado el router en FastAPI:

### Gestión de Instancias
- `POST /whatsapp/instances` - Crear instancia
- `GET /whatsapp/instances` - Listar instancias
- `GET /whatsapp/qr/{instance}` - Obtener QR code
- `GET /whatsapp/status/{instance}` - Verificar estado
- `DELETE /whatsapp/instances/{instance}` - Eliminar instancia

### Mensajes
- `POST /whatsapp/send-text` - Enviar texto
- `POST /whatsapp/send-image` - Enviar imagen
- `POST /whatsapp/send-document` - Enviar documento

## Pruebas

Ver [test_whatsapp.py](../tests/whatsapp/test_whatsapp.py) en `paquetes/tests/whatsapp/`.

Ejecutar el script de pruebas:

```bash
# Desde el contenedor (recomendado)
docker exec api-mcp python3 -m paquetes.tests.whatsapp.test_whatsapp

# O directamente
docker exec api-mcp python3 paquetes/tests/whatsapp/test_whatsapp.py
```

El script verifica:
- ✓ Conexión a Evolution API
- ✓ Listado de instancias
- ✓ Creación de instancia
- ✓ Generación de QR code
- ✓ Formateo de números de teléfono

## Casos de Uso

### Notificaciones Automáticas

```python
from paquetes.evolution import EvolutionClient

# Configurar cliente
client = EvolutionClient()

async def notificar_pedido(pedido_id: int):
    """Notifica cuando se crea un pedido."""
    pedido = obtener_pedido(pedido_id)

    mensaje = f"""
    ✅ Pedido #{pedido.id} confirmado

    Total: ${pedido.total}
    Entrega: {pedido.fecha_entrega}

    ¡Gracias por tu compra!
    """

    client.send_text(
        "ventas",
        pedido.cliente_telefono,
        mensaje
    )
```

### Alertas del Sistema

```python
from paquetes.evolution import EvolutionClient

client = EvolutionClient()

async def alertar_error_critico(error: str):
    """Alerta al admin sobre errores críticos."""
    mensaje = f"🚨 ERROR CRÍTICO: {error}"

    client.send_text(
        "admin",
        "5215512345678",  # Número del admin
        mensaje
    )
```

### Reportes Programados

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from paquetes.evolution import EvolutionClient

client = EvolutionClient()
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=8, minute=0)  # Diario a las 8am
async def enviar_reporte_diario():
    """Envía reporte de ventas diario."""
    reporte = generar_reporte_ventas_diario()

    mensaje = f"""
    📊 Reporte Diario de Ventas

    Ventas: {reporte.total_ventas}
    Pedidos: {reporte.num_pedidos}
    Tickets promedio: ${reporte.ticket_promedio}
    """

    client.send_text(
        "reportes",
        "5215512345678",
        mensaje
    )
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│ FastAPI App (api-mcp:8000)                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌─────────────────────┐      │
│  │router.py     │ ◄─────► │client.py            │      │
│  │(endpoints)   │         │(wrapper)            │      │
│  └──────────────┘         └──────────┬──────────┘      │
│                                       │ hereda           │
│                           ┌───────────▼──────────┐      │
│                           │evolution/            │      │
│                           │EvolutionClient       │      │
│                           │(cliente genérico)    │      │
│                           └──────────┬───────────┘      │
│                                      │                   │
└──────────────────────────────────────┼───────────────────┘
                                       │ HTTP
                                       ▼
                       ┌───────────────────────────┐
                       │ evolution-api-mcp:8080    │
                       │ (Evolution API v2.3.6)    │
                       └──────┬──────────┬─────────┘
                              │          │
                      ┌───────▼──┐   ┌──▼─────┐
                      │PostgreSQL│   │ Redis  │
                      │(evolutiondb) │(sesiones)│
                      └──────────┘   └────────┘
```

### Relación con Evolution

- **[evolution](../evolution/README.md)**: Paquete genérico y portable con 14 funciones core (sin valores hardcodeados)
- **whatsapp**: Wrapper genérico + router FastAPI + métodos adicionales (webhooks)
- **Ventajas**: DRY (sin duplicación), mantenibilidad, portabilidad, separación de responsabilidades

**Ambos módulos son completamente genéricos y portables**. No contienen valores hardcodeados.

## Configuración

### Variables de Entorno (REQUERIDAS)

En `.env.api-mcp`:

```bash
# Evolution API (REQUERIDO - sin valores por defecto)
EVOLUTION_API_URL=http://evolution-api-mcp:8080
EVOLUTION_API_KEY=tu_api_key_segura_aqui
```

**Importante:** Este módulo es completamente genérico y NO tiene valores por defecto hardcodeados. Debes configurar estas variables antes de usar el paquete.

### Múltiples Instancias

Puedes tener múltiples números de WhatsApp conectados:

```python
from paquetes.evolution import EvolutionClient

# Crear cliente
client = EvolutionClient()

# Crear instancias para diferentes propósitos
client.create_instance("ventas")
client.create_instance("soporte")
client.create_instance("admin")

# Usar instancias específicas
client.send_text("ventas", "521...", "Mensaje de ventas")
client.send_text("soporte", "521...", "Mensaje de soporte")
```

## Troubleshooting

### Error: Evolution API client no configurado

**Causa:** El router fue usado sin configurar el cliente.

**Solución:**
```python
from paquetes.whatsapp import set_evolution_client
from paquetes.evolution import EvolutionClient

# Configurar cliente antes de usar el router
client = EvolutionClient()
set_evolution_client(client)
```

### Error: Evolution API URL no configurada

**Causa:** No se configuró `EVOLUTION_API_URL` en `.env`

**Solución:**
```bash
# Agregar a .env
EVOLUTION_API_URL=http://evolution-api-mcp:8080
```

### Error: Evolution API Key no configurada

**Causa:** No se configuró `EVOLUTION_API_KEY` en `.env`

**Solución:**
```bash
# Generar y agregar a .env
openssl rand -hex 32
# Copiar output y agregarlo a .env
EVOLUTION_API_KEY=<output_del_comando>
```

### Error: Module 'requests' not found

```bash
docker exec api-mcp pip3 install requests
```

### Error: Instance not connected

1. Obtener QR: `GET /whatsapp/qr/{instance}`
2. Escanear con WhatsApp móvil
3. Verificar: `GET /whatsapp/status/{instance}`

### Mensaje no se envía

- Verificar que la instancia esté conectada (estado: "open")
- Verificar formato del número (debe incluir código de país)
- Verificar que el número exista en WhatsApp

### Evolution API no responde

```bash
# Verificar que esté corriendo
docker ps | grep evolution-api-mcp

# Ver logs
docker logs evolution-api-mcp --tail 100

# Reiniciar si es necesario
docker restart evolution-api-mcp
```

## Documentación

- [Guía de Integración Completa](INTEGRATION_EXAMPLES.md)
- [Módulo Evolution (base)](../evolution/README.md) - Cliente genérico de Evolution API
- [Evolution API Docs](https://doc.evolution-api.com/v2/)
- [Guía Evolution API](../../../../infraestructura/EVOLUTION_API_GUIA.md)

## Seguridad

- **NO** hardcodees API Keys en el código
- Usa variables de entorno para credenciales
- Genera API Keys seguras con `openssl rand -hex 32`
- Rota API Keys periódicamente
- Solo el contenedor `api-mcp` puede acceder a Evolution API (red interna)
- Los endpoints de FastAPI pueden requerir autenticación según tu configuración

## Estado de Tests

✓ Cliente Python - OK
✓ Conexión a Evolution API - OK
✓ Crear instancia - OK
✓ Obtener QR code - OK
✓ Formateo de números - OK
✓ Envío de mensajes - Requiere QR escaneado

## Próximos Pasos

1. Configurar variables de entorno en `.env`
2. Integrar el router en `main.py` y configurar cliente
3. Crear una instancia de WhatsApp
4. Escanear el QR code
5. Probar envío de mensajes
6. Integrar en tu lógica de negocio

## Licencia

Parte del sistema Backend API, MCP y Utilidades.

---

**Versión:** 2.0.0
**Última actualización:** 2026-01-31
**Base:** [evolution](../evolution/README.md) v1.0.0
**Tipo:** Módulo genérico y portable (sin valores hardcodeados)
