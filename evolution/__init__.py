"""
Módulo Evolution API - Cliente genérico para Evolution API (WhatsApp Multi-Instancia).

Este módulo es completamente genérico y portable.
NO tiene valores por defecto hardcodeados.

Características:
- Gestión de instancias: crear, listar, eliminar
- Envío de mensajes: texto, imágenes, documentos
- Verificación de estado de conexión
- Obtención de QR codes para vinculación

Requiere:
- requests (pip install requests)

Variables de entorno requeridas:
- EVOLUTION_API_URL: URL base de Evolution API (ej: http://localhost:8080)
- EVOLUTION_API_KEY: API Key para autenticación

Documentación oficial: https://doc.evolution-api.com/v2/
"""

from .evolution_client import (
    EvolutionClient,
    get_evolution_client
)

__all__ = [
    # Cliente principal
    "EvolutionClient",
    "get_evolution_client",
]

__version__ = "1.0.0"
