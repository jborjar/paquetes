"""
Cliente genérico para Evolution API - Gestión de instancias WhatsApp multi-instancia.

Este módulo es completamente genérico y portable.
NO tiene valores por defecto hardcodeados.

Documentación oficial: https://doc.evolution-api.com/v2/
"""
import os
import requests
from typing import Optional, Dict, List, Any


class EvolutionClient:
    """
    Cliente genérico para interactuar con Evolution API.

    Permite gestionar instancias de WhatsApp y enviar mensajes.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Inicializa el cliente de Evolution API.

        Args:
            base_url: URL base de Evolution API (default: lee EVOLUTION_API_URL del .env)
            api_key: API Key para autenticación (default: lee EVOLUTION_API_KEY del .env)
            timeout: Timeout para requests en segundos (default: 30)

        Raises:
            ValueError: Si no se proporciona base_url ni API_KEY
        """
        self.base_url = (base_url or os.getenv("EVOLUTION_API_URL", "")).rstrip('/')
        self.api_key = api_key or os.getenv("EVOLUTION_API_KEY")
        self.timeout = timeout

        if not self.base_url:
            raise ValueError(
                "Evolution API URL no configurada. "
                "Proporciona 'base_url' o configura EVOLUTION_API_URL en .env"
            )

        if not self.api_key:
            raise ValueError(
                "Evolution API Key no configurada. "
                "Proporciona 'api_key' o configura EVOLUTION_API_KEY en .env"
            )

        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Realiza una petición HTTP a Evolution API.

        Args:
            method: Método HTTP (GET, POST, DELETE, PUT)
            endpoint: Endpoint de la API (sin slash inicial)
            data: Datos a enviar en el body (para POST/PUT)
            params: Parámetros de query string

        Returns:
            Respuesta JSON de la API

        Raises:
            requests.HTTPError: Si la petición falla
            requests.RequestException: Si hay error de conexión
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Intentar parsear JSON, si falla retornar texto
            try:
                return response.json()
            except ValueError:
                return {"message": response.text, "status_code": response.status_code}

        except requests.RequestException as e:
            raise requests.RequestException(
                f"Error al conectar con Evolution API: {str(e)}"
            ) from e

    # ============================================
    # GESTIÓN DE INSTANCIAS
    # ============================================

    def list_instances(self) -> List[Dict[str, Any]]:
        """
        Lista todas las instancias de WhatsApp configuradas.

        Returns:
            Lista de instancias con su información

        Example:
            >>> client = EvolutionClient()
            >>> instances = client.list_instances()
            >>> for inst in instances:
            ...     print(f"{inst['instanceName']}: {inst['connectionStatus']}")
        """
        return self._request("GET", "instance/fetchInstances")

    def create_instance(
        self,
        instance_name: str,
        qrcode: bool = True,
        integration: str = "WHATSAPP-BAILEYS",
        webhook_url: Optional[str] = None,
        webhook_events: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva instancia de WhatsApp.

        Args:
            instance_name: Nombre único para la instancia
            qrcode: Si debe generar QR code (default: True)
            integration: Tipo de integración (default: WHATSAPP-BAILEYS)
            webhook_url: URL para recibir webhooks (opcional)
            webhook_events: Eventos que disparan webhook (opcional)

        Returns:
            Información de la instancia creada con QR code si aplica

        Example:
            >>> client = EvolutionClient()
            >>> result = client.create_instance("mi_whatsapp")
            >>> print(result['qrcode']['code'])  # Mostrar QR code
        """
        payload = {
            "instanceName": instance_name,
            "qrcode": qrcode,
            "integration": integration
        }

        if webhook_url:
            payload["webhook"] = {
                "url": webhook_url,
                "events": webhook_events or ["messages.upsert"]
            }

        return self._request("POST", "instance/create", data=payload)

    def delete_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Elimina una instancia de WhatsApp.

        Args:
            instance_name: Nombre de la instancia a eliminar

        Returns:
            Confirmación de eliminación

        Example:
            >>> client = EvolutionClient()
            >>> result = client.delete_instance("mi_whatsapp")
            >>> print(result['message'])
        """
        return self._request("DELETE", f"instance/delete/{instance_name}")

    def get_instance_info(self, instance_name: str) -> Dict[str, Any]:
        """
        Obtiene información detallada de una instancia.

        Args:
            instance_name: Nombre de la instancia

        Returns:
            Información completa de la instancia

        Example:
            >>> client = EvolutionClient()
            >>> info = client.get_instance_info("mi_whatsapp")
            >>> print(f"Estado: {info['connectionStatus']}")
        """
        return self._request("GET", f"instance/connectionState/{instance_name}")

    def get_qr_code(self, instance_name: str) -> Dict[str, Any]:
        """
        Obtiene el código QR de una instancia para vincularla.

        Args:
            instance_name: Nombre de la instancia

        Returns:
            QR code en base64 y texto

        Example:
            >>> client = EvolutionClient()
            >>> qr = client.get_qr_code("mi_whatsapp")
            >>> print(qr['code'])  # Código QR en texto
        """
        return self._request("GET", f"instance/connect/{instance_name}")

    def logout_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Desconecta una instancia de WhatsApp (cierra sesión).

        Args:
            instance_name: Nombre de la instancia

        Returns:
            Confirmación de desconexión

        Example:
            >>> client = EvolutionClient()
            >>> result = client.logout_instance("mi_whatsapp")
        """
        return self._request("DELETE", f"instance/logout/{instance_name}")

    def restart_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Reinicia una instancia de WhatsApp.

        Args:
            instance_name: Nombre de la instancia

        Returns:
            Confirmación de reinicio

        Example:
            >>> client = EvolutionClient()
            >>> result = client.restart_instance("mi_whatsapp")
        """
        return self._request("PUT", f"instance/restart/{instance_name}")

    # ============================================
    # ENVÍO DE MENSAJES
    # ============================================

    def send_text(
        self,
        instance_name: str,
        number: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto.

        Args:
            instance_name: Nombre de la instancia desde la cual enviar
            number: Número de teléfono destino (formato: 5215512345678)
            text: Texto del mensaje

        Returns:
            Confirmación de envío con message_id

        Example:
            >>> client = EvolutionClient()
            >>> result = client.send_text("mi_whatsapp", "5215512345678", "Hola!")
            >>> print(result['key']['id'])  # Message ID
        """
        # Asegurar formato correcto del número
        number = self._format_phone_number(number)

        payload = {
            "number": number,
            "text": text
        }

        return self._request(
            "POST",
            f"message/sendText/{instance_name}",
            data=payload
        )

    def send_media(
        self,
        instance_name: str,
        number: str,
        media_url: str,
        media_type: str = "image",
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía un archivo multimedia (imagen, video, audio, documento).

        Args:
            instance_name: Nombre de la instancia
            number: Número de teléfono destino
            media_url: URL del archivo a enviar
            media_type: Tipo de medio (image, video, audio, document)
            caption: Texto opcional del mensaje
            filename: Nombre del archivo (requerido para documentos)

        Returns:
            Confirmación de envío

        Example:
            >>> client = EvolutionClient()
            >>> result = client.send_media(
            ...     "mi_whatsapp",
            ...     "5215512345678",
            ...     "https://ejemplo.com/imagen.jpg",
            ...     media_type="image",
            ...     caption="Mira esta imagen"
            ... )
        """
        number = self._format_phone_number(number)

        payload = {
            "number": number,
            "mediatype": media_type,
            "media": media_url
        }

        if caption:
            payload["caption"] = caption

        if filename:
            payload["fileName"] = filename

        return self._request(
            "POST",
            f"message/sendMedia/{instance_name}",
            data=payload
        )

    def send_image(
        self,
        instance_name: str,
        number: str,
        image_url: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía una imagen (atajo para send_media).

        Args:
            instance_name: Nombre de la instancia
            number: Número de teléfono destino
            image_url: URL de la imagen
            caption: Texto opcional

        Returns:
            Confirmación de envío

        Example:
            >>> client = EvolutionClient()
            >>> result = client.send_image(
            ...     "mi_whatsapp",
            ...     "5215512345678",
            ...     "https://ejemplo.com/foto.jpg",
            ...     caption="Nueva foto"
            ... )
        """
        return self.send_media(
            instance_name=instance_name,
            number=number,
            media_url=image_url,
            media_type="image",
            caption=caption
        )

    def send_document(
        self,
        instance_name: str,
        number: str,
        document_url: str,
        filename: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía un documento (atajo para send_media).

        Args:
            instance_name: Nombre de la instancia
            number: Número de teléfono destino
            document_url: URL del documento
            filename: Nombre del archivo
            caption: Texto opcional

        Returns:
            Confirmación de envío

        Example:
            >>> client = EvolutionClient()
            >>> result = client.send_document(
            ...     "mi_whatsapp",
            ...     "5215512345678",
            ...     "https://ejemplo.com/reporte.pdf",
            ...     "Reporte_Mensual.pdf"
            ... )
        """
        return self.send_media(
            instance_name=instance_name,
            number=number,
            media_url=document_url,
            media_type="document",
            caption=caption,
            filename=filename
        )

    # ============================================
    # UTILIDADES
    # ============================================

    def _format_phone_number(self, phone: str, country_code: str = "52") -> str:
        """
        Formatea un número de teléfono al formato de WhatsApp.

        Args:
            phone: Número de teléfono
            country_code: Código de país (default: 52 para México)

        Returns:
            Número formateado (ej: 5215512345678)

        Example:
            >>> client = EvolutionClient()
            >>> formatted = client._format_phone_number("5512345678")
            >>> print(formatted)  # "5215512345678"
        """
        # Limpiar espacios y caracteres especiales
        phone = ''.join(filter(str.isdigit, phone))

        # Si ya tiene código de país, retornar
        if phone.startswith(country_code):
            return phone

        # Agregar código de país
        return f"{country_code}{phone}"

    def is_instance_connected(self, instance_name: str) -> bool:
        """
        Verifica si una instancia está conectada.

        Args:
            instance_name: Nombre de la instancia

        Returns:
            True si está conectada, False si no

        Example:
            >>> client = EvolutionClient()
            >>> if client.is_instance_connected("mi_whatsapp"):
            ...     print("WhatsApp conectado")
        """
        try:
            info = self.get_instance_info(instance_name)
            return info.get("state") == "open" or info.get("connectionStatus") == "open"
        except Exception:
            return False

    def get_instance_status(self, instance_name: str) -> str:
        """
        Obtiene el estado de conexión de una instancia.

        Args:
            instance_name: Nombre de la instancia

        Returns:
            Estado de la instancia (open, close, connecting, etc.)

        Example:
            >>> client = EvolutionClient()
            >>> status = client.get_instance_status("mi_whatsapp")
            >>> print(f"Estado: {status}")
        """
        try:
            info = self.get_instance_info(instance_name)
            return info.get("state") or info.get("connectionStatus", "unknown")
        except Exception:
            return "error"


# ============================================
# FUNCIONES DE CONVENIENCIA
# ============================================

def get_evolution_client(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> EvolutionClient:
    """
    Crea una instancia de EvolutionClient con configuración de entorno.

    Args:
        base_url: URL base (opcional, lee de .env)
        api_key: API Key (opcional, lee de .env)

    Returns:
        Cliente configurado

    Example:
        >>> from evolution import get_evolution_client
        >>> client = get_evolution_client()
        >>> instances = client.list_instances()
    """
    return EvolutionClient(base_url=base_url, api_key=api_key)
