"""
Construcción de queries OData para SAP Business One Service Layer.

Proporciona funciones helper para construir filtros, selecciones, etc.
"""
from typing import Dict, List, Optional, Any, Union
from .sl_crud import query_entities


def build_filter(conditions: Dict[str, Any], operator: str = 'and') -> str:
    """
    Construye un string de filtro OData desde un diccionario.

    Args:
        conditions: Diccionario con campo: valor
        operator: Operador lógico ('and' o 'or')

    Returns:
        String de filtro OData

    Example:
        >>> # Filtro simple
        >>> filter_str = build_filter({'CardType': 'cSupplier', 'Valid': 'tYES'})
        >>> print(filter_str)
        "CardType eq 'cSupplier' and Valid eq 'tYES'"
        >>>
        >>> # Filtro con OR
        >>> filter_str = build_filter({'CardType': 'cSupplier'}, operator='or')
    """
    if not conditions:
        return ''

    filters = []
    for field, value in conditions.items():
        # Valores string van con comillas simples
        if isinstance(value, str):
            filters.append(f"{field} eq '{value}'")
        # Números sin comillas
        elif isinstance(value, (int, float)):
            filters.append(f"{field} eq {value}")
        # Booleanos
        elif isinstance(value, bool):
            filters.append(f"{field} eq {str(value).lower()}")
        # None se maneja como null
        elif value is None:
            filters.append(f"{field} eq null")

    return f" {operator} ".join(filters)


def build_select(fields: List[str]) -> str:
    """
    Construye un string de selección de campos.

    Args:
        fields: Lista de campos a seleccionar

    Returns:
        String separado por comas

    Example:
        >>> select_str = build_select(['ItemCode', 'ItemName', 'Price'])
        >>> print(select_str)
        'ItemCode,ItemName,Price'
    """
    return ','.join(fields)


def build_expand(relations: List[str]) -> str:
    """
    Construye un string de expansión de relaciones.

    Args:
        relations: Lista de relaciones a expandir

    Returns:
        String separado por comas

    Example:
        >>> expand_str = build_expand(['BusinessPartnerAddresses', 'ContactEmployees'])
        >>> print(expand_str)
        'BusinessPartnerAddresses,ContactEmployees'
    """
    return ','.join(relations)


def build_orderby(fields: Dict[str, str]) -> str:
    """
    Construye un string de ordenamiento.

    Args:
        fields: Diccionario con campo: dirección ('asc' o 'desc')

    Returns:
        String de ordenamiento OData

    Example:
        >>> orderby_str = build_orderby({'ItemName': 'asc', 'Price': 'desc'})
        >>> print(orderby_str)
        'ItemName asc,Price desc'
    """
    if not fields:
        return ''

    order_clauses = []
    for field, direction in fields.items():
        if direction.lower() not in ('asc', 'desc'):
            direction = 'asc'
        order_clauses.append(f"{field} {direction.lower()}")

    return ','.join(order_clauses)


def execute_query(
    entity_name: str,
    conditions: Optional[Dict[str, Any]] = None,
    select_fields: Optional[List[str]] = None,
    order_by: Optional[Dict[str, str]] = None,
    expand_relations: Optional[List[str]] = None,
    top: Optional[int] = None,
    skip: Optional[int] = None,
    inlinecount: bool = False,
    max_page_size: int = 0,
    filter_operator: str = 'and',
    url: Optional[str] = None,
    session: Optional[Dict] = None
):
    """
    Ejecuta una query completa con construcción automática de parámetros OData.

    Esta es una función de alto nivel que combina todas las utilidades.

    Args:
        entity_name: Nombre de la entidad
        conditions: Condiciones de filtro como diccionario
        select_fields: Campos a seleccionar
        order_by: Ordenamiento como diccionario
        expand_relations: Relaciones a expandir
        top: Límite de registros
        skip: Registros a saltar
        inlinecount: Si True, incluye total count (default: False)
        max_page_size: Tamaño máximo de página (0 = sin límite, default: 0)
        filter_operator: Operador lógico para conditions ('and' o 'or')
        url: URL base del Service Layer (opcional)
        session: Sesión activa (opcional)

    Returns:
        Si inlinecount=False: Lista de entidades
        Si inlinecount=True: Dict con 'value' y 'count'

    Example:
        >>> # Query completa obteniendo todos los registros (sin límite)
        >>> items = execute_query(
        ...     entity_name='Items',
        ...     conditions={'ItemType': 'itItems', 'Valid': 'tYES'},
        ...     select_fields=['ItemCode', 'ItemName', 'Price'],
        ...     order_by={'ItemName': 'asc'}
        ... )
        >>>
        >>> # Con inlinecount para obtener total
        >>> result = execute_query(
        ...     'BusinessPartners',
        ...     conditions={'CardType': 'cSupplier'},
        ...     inlinecount=True
        ... )
        >>> print(f"Total proveedores: {result['count']}")
        >>>
        >>> # Con límite de página personalizado
        >>> items_paginados = execute_query(
        ...     'Items',
        ...     max_page_size=100
        ... )
    """
    # Construir parámetros
    filter_str = None
    if conditions:
        filter_str = build_filter(conditions, filter_operator)

    select_str = None
    if select_fields:
        select_str = build_select(select_fields)

    orderby_str = None
    if order_by:
        orderby_str = build_orderby(order_by)

    expand_str = None
    if expand_relations:
        expand_str = build_expand(expand_relations)

    # Ejecutar query
    return query_entities(
        entity_name=entity_name,
        filter=filter_str,
        select=select_str,
        orderby=orderby_str,
        expand=expand_str,
        top=top,
        skip=skip,
        inlinecount=inlinecount,
        max_page_size=max_page_size,
        url=url,
        session=session
    )
