"""
Módulo SAP Business One Service Layer - Cliente REST API genérico.

Este módulo proporciona un cliente completo para SAP B1 Service Layer:
- Autenticación (login/logout, gestión de sesiones)
- CRUD (GET, POST, PATCH, DELETE)
- Queries OData ($filter, $select, $expand, $orderby, $top, $skip)

⚠️ MÓDULO GENÉRICO: Sin valores por defecto hardcodeados.
   Las credenciales se obtienen de variables de entorno o parámetros.

Variables de entorno requeridas:
- SAP_B1_SERVICE_LAYER_URL: URL base del Service Layer (ej: https://server:50000/b1s/v1)
- SAP_B1_USER: Usuario de SAP B1
- SAP_B1_PASSWORD: Contraseña
- SAP_B1_COMPANY_DB: Base de datos de la compañía (opcional)
"""

# Autenticación
from .sl_auth import (
    login,
    logout,
    get_session,
    is_session_active
)

# CRUD
from .sl_crud import (
    get_entity,
    query_entities,
    create_entity,
    update_entity,
    delete_entity,
    batch_request
)

# Queries OData
from .sl_queries import (
    build_filter,
    build_select,
    build_expand,
    build_orderby,
    execute_query
)

__all__ = [
    # === Autenticación ===
    "login",
    "logout",
    "get_session",
    "is_session_active",

    # === CRUD ===
    "get_entity",
    "query_entities",
    "create_entity",
    "update_entity",
    "delete_entity",
    "batch_request",

    # === Queries OData ===
    "build_filter",
    "build_select",
    "build_expand",
    "build_orderby",
    "execute_query"
]
