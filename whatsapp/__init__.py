"""
Paquete WhatsApp - Evolution API Integration.

Este paquete proporciona integración completa con Evolution API para envío
de mensajes de WhatsApp desde la aplicación FastAPI.

⚠️ **MÓDULO GENÉRICO**: Este módulo NO tiene valores por defecto hardcodeados.
El usuario debe proporcionar TODAS las variables de conexión en el archivo .env
o pasarlas explícitamente al crear el cliente.

Variables de entorno requeridas:
- EVOLUTION_API_URL: URL base de Evolution API (ej: http://localhost:8080)
- EVOLUTION_API_KEY: API Key para autenticación

Componentes principales:
- EvolutionAPIClient: Cliente para interactuar con Evolution API (hereda de evolution.EvolutionClient)
- router: Router de FastAPI con endpoints REST
- MessageType: Enum con tipos de mensajes soportados

Uso básico:
    from paquetes.whatsapp import EvolutionAPIClient, router

    # Crear cliente (lee de .env)
    client = EvolutionAPIClient()

    # O con parámetros explícitos
    client = EvolutionAPIClient(
        base_url="http://localhost:8080",
        api_key="your_api_key"
    )

    # Usar cliente
    client.send_text("instancia", "5215512345678", "Hola!")

    # Agregar router a FastAPI
    app.include_router(router)

Documentación:
    Ver README.md en este directorio para guía completa.
"""
from .client import EvolutionAPIClient, MessageType
from .router import router, set_evolution_client

__all__ = [
    "EvolutionAPIClient",
    "MessageType",
    "router",
    "set_evolution_client",
]

__version__ = "2.0.0"
