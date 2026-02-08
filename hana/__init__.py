"""
Módulo SAP HANA - Operaciones completas para SAP HANA Database.

Este módulo proporciona funciones organizadas según el estándar SQL:
- DML (Data Manipulation Language) - Manipulación de datos
- DDL (Data Definition Language) - Definición de estructura
- DCL (Data Control Language) - Control de acceso y permisos
"""

# DML - Data Manipulation Language (hana_dml.py)
from .hana_dml import (
    get_hana_connection,
    insert,
    insert_many,
    select,
    select_one,
    update,
    delete,
    exists,
    count,
    execute_query,
    upsert,
    truncate,
    get_table_columns
)

# DDL - Data Definition Language (hana_ddl.py)
from .hana_ddl import (
    schema_exists,
    get_schemas,
    table_exists,
    create_table,
    drop_table,
    truncate_table,
    execute_ddl,
    create_index,
    drop_index
)

# DCL - Data Control Language (hana_dcl.py)
from .hana_dcl import (
    # Usuarios
    user_exists,
    create_user,
    drop_user,
    # Permisos
    grant_permission,
    revoke_permission,
    get_user_permissions,
    # Roles
    role_exists,
    create_role,
    drop_role,
    grant_role,
    revoke_role,
    get_user_roles,
    # Conexiones
    get_active_connections,
    get_connection_count,
    # Utilidades
    create_readonly_user,
    create_readwrite_user
)

__all__ = [
    # Conexión
    "get_hana_connection",

    # === DML - Data Manipulation Language ===
    "insert",
    "insert_many",
    "select",
    "select_one",
    "update",
    "delete",
    "exists",
    "count",
    "execute_query",
    "upsert",
    "truncate",
    "get_table_columns",

    # === DDL - Data Definition Language ===
    # Schemas y Tablas
    "schema_exists",
    "get_schemas",
    "table_exists",
    "create_table",
    "drop_table",
    "truncate_table",
    # Índices y DDL personalizado
    "execute_ddl",
    "create_index",
    "drop_index",

    # === DCL - Data Control Language ===
    # Usuarios
    "user_exists",
    "create_user",
    "drop_user",
    # Permisos
    "grant_permission",
    "revoke_permission",
    "get_user_permissions",
    # Roles
    "role_exists",
    "create_role",
    "drop_role",
    "grant_role",
    "revoke_role",
    "get_user_roles",
    # Conexiones
    "get_active_connections",
    "get_connection_count",
    # Utilidades de seguridad
    "create_readonly_user",
    "create_readwrite_user"
]
