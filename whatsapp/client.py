"""
Cliente para Evolution API - WhatsApp Multi-Instancia
Wrapper genérico sobre el módulo evolution.

Este módulo es completamente genérico y portable.
NO tiene valores por defecto hardcodeados.

Documentación: https://doc.evolution-api.com/v2/
"""
from typing import Optional, Dict, List, Any
from enum import Enum

from ..evolution import EvolutionClient


class MessageType(Enum):
    """Tipos de mensajes soportados por Evolution API."""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"


class EvolutionAPIClient(EvolutionClient):
    """
    Cliente para interactuar con Evolution API.

    Esta clase extiende EvolutionClient con funcionalidad adicional específica
    para el uso en este proyecto (webhooks), pero sin valores hardcodeados.

    Todos los parámetros deben proporcionarse explícitamente o via variables
    de entorno (.env).
    """

    # ======================
    # Webhooks (extensión de EvolutionClient)
    # ======================

    def set_webhook(
        self,
        instance_name: str,
        webhook_url: str,
        events: Optional[List[str]] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Configura un webhook para recibir eventos.

        Args:
            instance_name: Nombre de la instancia
            webhook_url: URL donde recibir los eventos
            events: Lista de eventos a suscribirse
            enabled: Si el webhook está habilitado

        Returns:
            Configuración del webhook

        Example:
            >>> client = EvolutionAPIClient(
            ...     base_url="http://localhost:8080",
            ...     api_key="your_key"
            ... )
            >>> client.set_webhook(
            ...     "mi_whatsapp",
            ...     "https://mi-servidor.com/webhook",
            ...     events=["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
            ... )
        """
        if events is None:
            events = [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "CONNECTION_UPDATE"
            ]

        data = {
            "url": webhook_url,
            "enabled": enabled,
            "events": events
        }

        return self._request("POST", f"/webhook/set/{instance_name}", data=data)

    # ======================
    # Alias de compatibilidad
    # ======================

    def format_phone_number(self, phone: str, country_code: str = "52") -> str:
        """
        Alias de _format_phone_number para compatibilidad con código existente.

        Args:
            phone: Número de teléfono (puede contener espacios, guiones, etc.)
            country_code: Código de país (default: 52 para México)

        Returns:
            Número formateado (ejemplo: 5215512345678)

        Example:
            >>> client.format_phone_number("55 1234 5678")
            '5215512345678'
        """
        return self._format_phone_number(phone, country_code)

    def get_connection_state(self, instance_name: str) -> Dict[str, Any]:
        """
        Alias de get_instance_info para compatibilidad con código existente.

        Args:
            instance_name: Nombre de la instancia

        Returns:
            Estado de conexión (close, connecting, open)

        Example:
            >>> state = client.get_connection_state("mi_whatsapp")
            >>> print(state['state'])  # 'open' si está conectado
        """
        return self.get_instance_info(instance_name)
