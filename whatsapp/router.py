"""
Router de FastAPI para enviar mensajes de WhatsApp usando Evolution API.

⚠️ **MÓDULO GENÉRICO**: Este router NO crea un cliente por defecto.
El usuario debe configurar el cliente globalmente antes de usar el router.

Configuración requerida en tu aplicación (main.py):
    from paquetes.whatsapp import router
    from paquetes.whatsapp.router import set_evolution_client
    from paquetes.evolution import EvolutionClient

    # Configurar cliente (lee de .env)
    client = EvolutionClient()
    set_evolution_client(client)

    # Agregar router
    app.include_router(router)

Endpoints disponibles:
- POST /whatsapp/send-text - Enviar mensaje de texto
- POST /whatsapp/send-image - Enviar imagen
- POST /whatsapp/send-document - Enviar documento
- GET /whatsapp/instances - Listar instancias
- GET /whatsapp/qr/{instance} - Obtener QR code
- GET /whatsapp/status/{instance} - Verificar estado de conexión
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from .client import EvolutionAPIClient, MessageType

# Configurar logging
logger = logging.getLogger(__name__)

# Cliente Evolution API (debe configurarse externamente)
_evolution_client: Optional[EvolutionAPIClient] = None


def set_evolution_client(client: EvolutionAPIClient) -> None:
    """
    Configura el cliente de Evolution API para el router.

    Esta función debe llamarse antes de usar el router.

    Args:
        client: Instancia configurada de EvolutionAPIClient

    Example:
        >>> from paquetes.evolution import EvolutionClient
        >>> from paquetes.whatsapp.router import set_evolution_client
        >>> client = EvolutionClient(
        ...     base_url="http://localhost:8080",
        ...     api_key="your_key"
        ... )
        >>> set_evolution_client(client)
    """
    global _evolution_client
    _evolution_client = client


def get_evolution_client() -> EvolutionAPIClient:
    """
    Obtiene el cliente de Evolution API configurado.

    Raises:
        RuntimeError: Si el cliente no ha sido configurado

    Returns:
        Cliente configurado de Evolution API
    """
    if _evolution_client is None:
        raise RuntimeError(
            "Evolution API client no configurado. "
            "Llama a set_evolution_client() antes de usar el router."
        )
    return _evolution_client


# Crear router
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


# ======================
# Modelos Pydantic
# ======================

class SendTextRequest(BaseModel):
    """Modelo para enviar mensaje de texto."""
    instance: str = Field(..., description="Nombre de la instancia de WhatsApp")
    number: str = Field(..., description="Número de teléfono (ej: 5215512345678 o 55 1234 5678)")
    message: str = Field(..., description="Texto del mensaje")
    delay: Optional[int] = Field(None, description="Delay en milisegundos antes de enviar")

    class Config:
        json_schema_extra = {
            "example": {
                "instance": "mi_whatsapp",
                "number": "5215512345678",
                "message": "Hola, este es un mensaje desde la API",
                "delay": 1000
            }
        }


class SendImageRequest(BaseModel):
    """Modelo para enviar imagen."""
    instance: str = Field(..., description="Nombre de la instancia de WhatsApp")
    number: str = Field(..., description="Número de teléfono")
    image_url: str = Field(..., description="URL de la imagen")
    caption: Optional[str] = Field(None, description="Texto que acompaña la imagen")

    class Config:
        json_schema_extra = {
            "example": {
                "instance": "mi_whatsapp",
                "number": "5215512345678",
                "image_url": "https://ejemplo.com/imagen.jpg",
                "caption": "Mira esta imagen"
            }
        }


class SendDocumentRequest(BaseModel):
    """Modelo para enviar documento."""
    instance: str = Field(..., description="Nombre de la instancia de WhatsApp")
    number: str = Field(..., description="Número de teléfono")
    document_url: str = Field(..., description="URL del documento")
    file_name: str = Field(..., description="Nombre del archivo")

    class Config:
        json_schema_extra = {
            "example": {
                "instance": "mi_whatsapp",
                "number": "5215512345678",
                "document_url": "https://ejemplo.com/documento.pdf",
                "file_name": "reporte.pdf"
            }
        }


class CreateInstanceRequest(BaseModel):
    """Modelo para crear instancia."""
    instance_name: str = Field(..., description="Nombre único para la instancia")
    integration: str = Field("WHATSAPP-BAILEYS", description="Tipo de integración")

    class Config:
        json_schema_extra = {
            "example": {
                "instance_name": "mi_whatsapp",
                "integration": "WHATSAPP-BAILEYS"
            }
        }


class MessageResponse(BaseModel):
    """Respuesta al enviar mensaje."""
    success: bool
    message: str
    data: Optional[dict] = None


# ======================
# Endpoints
# ======================

@router.post("/send-text", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def send_text_message(request: SendTextRequest):
    """
    Envía un mensaje de texto por WhatsApp.

    - **instance**: Nombre de la instancia configurada
    - **number**: Número de teléfono (se formatea automáticamente)
    - **message**: Texto a enviar
    - **delay**: Delay opcional antes de enviar (ms)
    """
    try:
        client = get_evolution_client()

        # Verificar que la instancia esté conectada
        if not client.is_instance_connected(request.instance):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La instancia '{request.instance}' no está conectada"
            )

        # Formatear número de teléfono
        formatted_number = client.format_phone_number(request.number)

        # Enviar mensaje
        result = client.send_text(
            instance_name=request.instance,
            number=formatted_number,
            text=request.message,
            delay=request.delay
        )

        logger.info(
            f"Mensaje enviado a {formatted_number} desde {request.instance}"
        )

        return MessageResponse(
            success=True,
            message="Mensaje enviado exitosamente",
            data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al enviar mensaje: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar mensaje: {str(e)}"
        )


@router.post("/send-image", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def send_image(request: SendImageRequest):
    """
    Envía una imagen por WhatsApp.

    - **instance**: Nombre de la instancia configurada
    - **number**: Número de teléfono
    - **image_url**: URL pública de la imagen
    - **caption**: Texto opcional que acompaña la imagen
    """
    try:
        client = get_evolution_client()

        if not client.is_instance_connected(request.instance):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La instancia '{request.instance}' no está conectada"
            )

        formatted_number = client.format_phone_number(request.number)

        result = client.send_image(
            instance_name=request.instance,
            number=formatted_number,
            image_url=request.image_url,
            caption=request.caption
        )

        logger.info(
            f"Imagen enviada a {formatted_number} desde {request.instance}"
        )

        return MessageResponse(
            success=True,
            message="Imagen enviada exitosamente",
            data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al enviar imagen: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar imagen: {str(e)}"
        )


@router.post("/send-document", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def send_document(request: SendDocumentRequest):
    """
    Envía un documento por WhatsApp.

    - **instance**: Nombre de la instancia configurada
    - **number**: Número de teléfono
    - **document_url**: URL pública del documento
    - **file_name**: Nombre que tendrá el archivo
    """
    try:
        client = get_evolution_client()

        if not client.is_instance_connected(request.instance):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La instancia '{request.instance}' no está conectada"
            )

        formatted_number = client.format_phone_number(request.number)

        result = client.send_document(
            instance_name=request.instance,
            number=formatted_number,
            document_url=request.document_url,
            file_name=request.file_name
        )

        logger.info(
            f"Documento enviado a {formatted_number} desde {request.instance}"
        )

        return MessageResponse(
            success=True,
            message="Documento enviado exitosamente",
            data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al enviar documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar documento: {str(e)}"
        )


@router.get("/instances", status_code=status.HTTP_200_OK)
async def list_instances():
    """
    Lista todas las instancias de WhatsApp configuradas.

    Retorna información de cada instancia incluyendo:
    - Nombre de la instancia
    - Estado de conexión
    - ID de la instancia
    """
    try:
        client = get_evolution_client()
        instances = client.list_instances()

        return {
            "success": True,
            "total": len(instances),
            "instances": instances
        }

    except Exception as e:
        logger.error(f"Error al listar instancias: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar instancias: {str(e)}"
        )


@router.get("/qr/{instance}", status_code=status.HTTP_200_OK)
async def get_qr_code(instance: str):
    """
    Obtiene el código QR para conectar una instancia.

    El QR se devuelve en formato base64 (data:image/png;base64,...)
    que puede mostrarse directamente en un <img> HTML.

    - **instance**: Nombre de la instancia
    """
    try:
        client = get_evolution_client()
        qr_data = client.get_qr_code(instance)

        return {
            "success": True,
            "instance": instance,
            "qr_code": qr_data.get('code'),
            "base64": qr_data.get('base64')
        }

    except Exception as e:
        logger.error(f"Error al obtener QR code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener QR code: {str(e)}"
        )


@router.get("/status/{instance}", status_code=status.HTTP_200_OK)
async def get_instance_status(instance: str):
    """
    Verifica el estado de conexión de una instancia.

    Estados posibles:
    - **close**: No conectado
    - **connecting**: Conectando...
    - **open**: Conectado y listo para enviar mensajes

    - **instance**: Nombre de la instancia
    """
    try:
        client = get_evolution_client()
        state = client.get_connection_state(instance)
        is_connected = state.get('state') == 'open'

        return {
            "success": True,
            "instance": instance,
            "state": state.get('state'),
            "connected": is_connected,
            "data": state
        }

    except Exception as e:
        logger.error(f"Error al verificar estado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar estado: {str(e)}"
        )


@router.post("/instances", status_code=status.HTTP_201_CREATED)
async def create_instance(request: CreateInstanceRequest):
    """
    Crea una nueva instancia de WhatsApp.

    Después de crear la instancia, usa el endpoint /qr/{instance}
    para obtener el código QR y conectar WhatsApp.

    - **instance_name**: Nombre único para identificar la instancia
    - **integration**: Tipo de integración (default: WHATSAPP-BAILEYS)
    """
    try:
        client = get_evolution_client()
        result = client.create_instance(
            instance_name=request.instance_name,
            integration=request.integration
        )

        logger.info(f"Instancia creada: {request.instance_name}")

        return {
            "success": True,
            "message": f"Instancia '{request.instance_name}' creada exitosamente",
            "data": result
        }

    except Exception as e:
        logger.error(f"Error al crear instancia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear instancia: {str(e)}"
        )


@router.delete("/instances/{instance}", status_code=status.HTTP_200_OK)
async def delete_instance(instance: str):
    """
    Elimina una instancia de WhatsApp.

    ADVERTENCIA: Esta acción elimina permanentemente la instancia
    y todos sus datos asociados.

    - **instance**: Nombre de la instancia a eliminar
    """
    try:
        client = get_evolution_client()
        result = client.delete_instance(instance)

        logger.info(f"Instancia eliminada: {instance}")

        return {
            "success": True,
            "message": f"Instancia '{instance}' eliminada exitosamente",
            "data": result
        }

    except Exception as e:
        logger.error(f"Error al eliminar instancia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar instancia: {str(e)}"
        )
