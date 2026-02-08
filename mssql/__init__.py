"""
Módulo MSSQL - Operaciones completas para SQL Server.

Este módulo proporciona funciones organizadas según el estándar SQL:
- DML (Data Manipulation Language) - Manipulación de datos
- DDL (Data Definition Language) - Definición de estructura
- DCL (Data Control Language) - Control de acceso y permisos
"""

# DML - Data Manipulation Language (mssql_dml.py)
from .mssql_dml import (
    get_mssql_connection,
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

# DDL - Data Definition Language (mssql_ddl.py)
from .mssql_ddl import (
    database_exists,
    create_database,
    drop_database,
    recreate_database,
    table_exists,
    create_table,
    drop_table,
    truncate_table,
    execute_ddl,
    create_index,
    drop_index
)

# DCL - Data Control Language (mssql_dcl.py)
from .mssql_dcl import (
    # Logins
    login_exists,
    create_login,
    drop_login,
    # Usuarios
    user_exists,
    create_user,
    drop_user,
    # Permisos
    grant_permission,
    revoke_permission,
    deny_permission,
    grant_table_permissions,
    get_user_permissions,
    # Roles
    role_exists,
    create_role,
    drop_role,
    add_user_to_role,
    remove_user_from_role,
    get_user_roles,
    # Utilidades
    create_readonly_user,
    create_readwrite_user,
    # Gestión de conexiones
    get_active_connections,
    kill_connection,
    kill_all_connections,
    get_connection_count
)

__all__ = [
    # Conexión
    "get_mssql_connection",

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
    # Bases de datos
    "database_exists",
    "create_database",
    "drop_database",
    "recreate_database",
    # Tablas
    "table_exists",
    "create_table",
    "drop_table",
    "truncate_table",
    # Índices y DDL personalizado
    "execute_ddl",
    "create_index",
    "drop_index",

    # === DCL - Data Control Language ===
    # Logins (server level)
    "login_exists",
    "create_login",
    "drop_login",
    # Usuarios (database level)
    "user_exists",
    "create_user",
    "drop_user",
    # Permisos
    "grant_permission",
    "revoke_permission",
    "deny_permission",
    "grant_table_permissions",
    "get_user_permissions",
    # Roles
    "role_exists",
    "create_role",
    "drop_role",
    "add_user_to_role",
    "remove_user_from_role",
    "get_user_roles",
    # Utilidades de seguridad
    "create_readonly_user",
    "create_readwrite_user",
    # Gestión de conexiones
    "get_active_connections",
    "kill_connection",
    "kill_all_connections",
    "get_connection_count"
]
