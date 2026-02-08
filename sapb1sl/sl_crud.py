"""
Operaciones CRUD para SAP Business One Service Layer.

Proporciona funciones genéricas para GET, POST, PATCH, DELETE.
"""
import requests
from typing import Dict, List, Optional, Any, Union
import urllib3
from .sl_auth import get_session

# Deshabilitar warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get_cookies(session: Dict[str, str]) -> Dict[str, str]:
    """Construye diccionario de cookies desde sesión."""
    cookies = {'B1SESSION': session['session_id']}
    if session.get('route_id'):
        cookies['ROUTEID'] = session['route_id']
    return cookies


def get_entity(
    entity_name: str,
    key: Any,
    select: Optional[str] = None,
    max_page_size: int = 0,
    url: Optional[str] = None,
    session: Optional[Dict] = None
) -> Dict:
    """
    Obtiene una entidad por su clave (GET).

    Args:
        entity_name: Nombre de la entidad (ej: 'Items', 'BusinessPartners')
        key: Clave primaria de la entidad (ej: 'A00001', 123)
        select: Campos a seleccionar (ej: 'ItemCode,ItemName')
        max_page_size: Tamaño máximo de página (0 = sin límite, default: 0)
        url: URL base del Service Layer (opcional)
        session: Sesión activa (opcional, se obtiene automáticamente)

    Returns:
        Dict con los datos de la entidad

    Raises:
        requests.exceptions.HTTPError: Si la entidad no existe o hay error

    Example:
        >>> # Obtener item por código
        >>> item = get_entity('Items', 'A00001')
        >>> print(item['ItemName'])
        >>>
        >>> # Con selección de campos
        >>> item = get_entity('Items', 'A00001', select='ItemCode,ItemName,Price')
    """
    # Obtener sesión
    if session is None:
        session = get_session(url=url)

    base_url = session['base_url']
    cookies = _get_cookies(session)

    # Construir URL
    # Para strings, usar comillas simples: Items('A00001')
    # Para números, sin comillas: Orders(123)
    if isinstance(key, str):
        entity_url = f"{base_url}/{entity_name}('{key}')"
    else:
        entity_url = f"{base_url}/{entity_name}({key})"

    # Agregar $select si está especificado
    params = {}
    if select:
        params['$select'] = select

    # Construir headers con odata.maxpagesize
    headers = {
        'Prefer': f'odata.maxpagesize={max_page_size}'
    }

    # Realizar GET
    response = requests.get(
        entity_url,
        params=params,
        cookies=cookies,
        headers=headers,
        verify=False,
        timeout=30
    )
    response.raise_for_status()

    return response.json()


def query_entities(
    entity_name: str,
    filter: Optional[str] = None,
    select: Optional[str] = None,
    orderby: Optional[str] = None,
    top: Optional[int] = None,
    skip: Optional[int] = None,
    expand: Optional[str] = None,
    inlinecount: bool = False,
    max_page_size: int = 0,
    url: Optional[str] = None,
    session: Optional[Dict] = None
):
    """
    Consulta múltiples entidades con filtros OData (GET).

    Args:
        entity_name: Nombre de la entidad (ej: 'Items')
        filter: Filtro OData (ej: "ItemType eq 'itItems'")
        select: Campos a seleccionar (ej: 'ItemCode,ItemName')
        orderby: Ordenamiento (ej: 'ItemName asc')
        top: Límite de registros
        skip: Registros a saltar (paginación)
        expand: Relaciones a expandir (ej: 'BusinessPartnerAddresses')
        inlinecount: Si True, incluye total count (default: False)
        max_page_size: Tamaño máximo de página (0 = sin límite, default: 0)
        url: URL base del Service Layer (opcional)
        session: Sesión activa (opcional)

    Returns:
        Si inlinecount=False: Lista de diccionarios con las entidades
        Si inlinecount=True: Dict con 'value' (lista) y 'count' (total)

    Example:
        >>> # Obtener todos los items activos (sin límite de página)
        >>> items = query_entities('Items', filter="Valid eq 'tYES'")
        >>>
        >>> # Con inlinecount para obtener total
        >>> result = query_entities('Items', filter="Valid eq 'tYES'", inlinecount=True)
        >>> print(f"Total: {result['count']}, Registros: {len(result['value'])}")
        >>>
        >>> # Con múltiples parámetros
        >>> partners = query_entities(
        ...     'BusinessPartners',
        ...     filter="CardType eq 'S'",
        ...     select='CardCode,CardName',
        ...     orderby='CardName asc',
        ...     inlinecount=True
        ... )
    """
    # Obtener sesión
    if session is None:
        session = get_session(url=url)

    base_url = session['base_url']
    cookies = _get_cookies(session)

    # Construir URL y parámetros
    entity_url = f"{base_url}/{entity_name}"
    params = {}

    if filter:
        params['$filter'] = filter
    if select:
        params['$select'] = select
    if orderby:
        params['$orderby'] = orderby
    if top is not None:
        params['$top'] = top
    if skip is not None:
        params['$skip'] = skip
    if expand:
        params['$expand'] = expand

    # Agregar inlinecount si se solicita
    if inlinecount:
        params['$inlinecount'] = 'allpages'

    # Construir headers con odata.maxpagesize
    headers = {
        'Prefer': f'odata.maxpagesize={max_page_size}'
    }

    # Realizar GET
    response = requests.get(
        entity_url,
        params=params,
        cookies=cookies,
        headers=headers,
        verify=False,
        timeout=30
    )
    response.raise_for_status()

    result = response.json()

    # Service Layer retorna {'value': [...]} para queries
    if isinstance(result, dict) and 'value' in result:
        # Si se solicitó inlinecount, retornar dict con value y count
        if inlinecount:
            return {
                'value': result['value'],
                'count': result.get('odata.count', len(result['value']))
            }
        # Sin inlinecount, retornar solo el array
        return result['value']

    return result


def create_entity(
    entity_name: str,
    data: Dict,
    url: Optional[str] = None,
    session: Optional[Dict] = None
) -> Dict:
    """
    Crea una nueva entidad (POST).

    Args:
        entity_name: Nombre de la entidad (ej: 'Items')
        data: Datos de la entidad a crear
        url: URL base del Service Layer (opcional)
        session: Sesión activa (opcional)

    Returns:
        Dict con la entidad creada

    Raises:
        requests.exceptions.HTTPError: Si falla la creación

    Example:
        >>> # Crear item
        >>> item_data = {
        ...     'ItemCode': 'A00001',
        ...     'ItemName': 'Producto Nuevo',
        ...     'ItemType': 'itItems'
        ... }
        >>> result = create_entity('Items', item_data)
        >>> print(result['ItemCode'])
    """
    # Obtener sesión
    if session is None:
        session = get_session(url=url)

    base_url = session['base_url']
    cookies = _get_cookies(session)

    # Construir URL
    entity_url = f"{base_url}/{entity_name}"

    # Realizar POST
    response = requests.post(
        entity_url,
        json=data,
        cookies=cookies,
        verify=False,
        timeout=60
    )
    response.raise_for_status()

    return response.json()


def update_entity(
    entity_name: str,
    key: Any,
    data: Dict,
    url: Optional[str] = None,
    session: Optional[Dict] = None
) -> bool:
    """
    Actualiza una entidad existente (PATCH).

    Args:
        entity_name: Nombre de la entidad (ej: 'Items')
        key: Clave primaria de la entidad
        data: Datos a actualizar
        url: URL base del Service Layer (opcional)
        session: Sesión activa (opcional)

    Returns:
        True si la actualización fue exitosa

    Raises:
        requests.exceptions.HTTPError: Si falla la actualización

    Example:
        >>> # Actualizar precio de item
        >>> update_entity('Items', 'A00001', {'Price': 150.00})
        True
    """
    # Obtener sesión
    if session is None:
        session = get_session(url=url)

    base_url = session['base_url']
    cookies = _get_cookies(session)

    # Construir URL
    if isinstance(key, str):
        entity_url = f"{base_url}/{entity_name}('{key}')"
    else:
        entity_url = f"{base_url}/{entity_name}({key})"

    # Realizar PATCH
    response = requests.patch(
        entity_url,
        json=data,
        cookies=cookies,
        verify=False,
        timeout=60
    )
    response.raise_for_status()

    return True


def delete_entity(
    entity_name: str,
    key: Any,
    url: Optional[str] = None,
    session: Optional[Dict] = None
) -> bool:
    """
    Elimina una entidad (DELETE).

    Args:
        entity_name: Nombre de la entidad
        key: Clave primaria de la entidad
        url: URL base del Service Layer (opcional)
        session: Sesión activa (opcional)

    Returns:
        True si la eliminación fue exitosa

    Raises:
        requests.exceptions.HTTPError: Si falla la eliminación

    Example:
        >>> delete_entity('Items', 'A00001')
        True
    """
    # Obtener sesión
    if session is None:
        session = get_session(url=url)

    base_url = session['base_url']
    cookies = _get_cookies(session)

    # Construir URL
    if isinstance(key, str):
        entity_url = f"{base_url}/{entity_name}('{key}')"
    else:
        entity_url = f"{base_url}/{entity_name}({key})"

    # Realizar DELETE
    response = requests.delete(
        entity_url,
        cookies=cookies,
        verify=False,
        timeout=30
    )
    response.raise_for_status()

    return True


def batch_request(
    requests_data: List[Dict],
    url: Optional[str] = None,
    session: Optional[Dict] = None
) -> List[Dict]:
    """
    Ejecuta múltiples operaciones en una sola llamada ($batch).

    Args:
        requests_data: Lista de operaciones a ejecutar
        url: URL base del Service Layer (opcional)
        session: Sesión activa (opcional)

    Returns:
        Lista con los resultados de cada operación

    Note:
        Esta es una función avanzada. Para operaciones simples,
        usar las funciones individuales (get_entity, create_entity, etc.)

    Example:
        >>> # Crear múltiples items en batch
        >>> batch_ops = [
        ...     {'method': 'POST', 'url': 'Items', 'data': {...}},
        ...     {'method': 'POST', 'url': 'Items', 'data': {...}}
        ... ]
        >>> results = batch_request(batch_ops)
    """
    # Obtener sesión
    if session is None:
        session = get_session(url=url)

    base_url = session['base_url']
    cookies = _get_cookies(session)

    # TODO: Implementar $batch según especificación OData
    # Esta es una característica avanzada que requiere construcción de multipart/mixed
    raise NotImplementedError(
        "batch_request no está implementado aún. "
        "Use operaciones individuales por ahora."
    )
