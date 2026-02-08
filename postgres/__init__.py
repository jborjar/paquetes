"""
Módulo PostgreSQL - Operaciones completas para PostgreSQL.

Este módulo proporciona funciones organizadas según el estándar SQL:
- DML (Data Manipulation Language) - Manipulación de datos
- DDL (Data Definition Language) - Definición de estructura
- DCL (Data Control Language) - Control de acceso y permisos
"""

# DML - Data Manipulation Language (postgres_dml.py)
from .postgres_dml import (
    get_postgres_connection,
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

# DDL - Data Definition Language (postgres_ddl.py)
from .postgres_ddl import (
    database_exists,
    create_database,
    drop_database,
    recreate_database,
    schema_exists,
    create_schema,
    drop_schema,
    table_exists,
    create_table,
    drop_table,
    truncate_table,
    execute_ddl,
    create_index,
    drop_index
)

# DCL - Data Control Language (postgres_dcl.py)
from .postgres_dcl import (
    # Roles y Usuarios
    role_exists,
    create_role,
    create_user,
    drop_role,
    drop_user,
    alter_role_password,
    # Permisos de Base de Datos
    grant_database_privileges,
    revoke_database_privileges,
    # Permisos de Schema
    grant_schema_privileges,
    revoke_schema_privileges,
    # Permisos de Tabla
    grant_table_privileges,
    revoke_table_privileges,
    grant_all_tables_in_schema,
    # Asignación de Roles
    grant_role_to_user,
    revoke_role_from_user,
    get_role_privileges,
    get_user_roles,
    # Utilidades
    create_readonly_user,
    create_readwrite_user,
    # Gestión de Conexiones
    get_active_connections,
    get_connection_count,
    terminate_connection,
    terminate_all_connections
)

__all__ = [
    # Conexión
    "get_postgres_connection",

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
    # Schemas
    "schema_exists",
    "create_schema",
    "drop_schema",
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
    # Roles y Usuarios
    "role_exists",
    "create_role",
    "create_user",
    "drop_role",
    "drop_user",
    "alter_role_password",
    # Permisos de Base de Datos
    "grant_database_privileges",
    "revoke_database_privileges",
    # Permisos de Schema
    "grant_schema_privileges",
    "revoke_schema_privileges",
    # Permisos de Tabla
    "grant_table_privileges",
    "revoke_table_privileges",
    "grant_all_tables_in_schema",
    # Asignación de Roles
    "grant_role_to_user",
    "revoke_role_from_user",
    "get_role_privileges",
    "get_user_roles",
    # Utilidades de seguridad
    "create_readonly_user",
    "create_readwrite_user",
    # Gestión de conexiones
    "get_active_connections",
    "get_connection_count",
    "terminate_connection",
    "terminate_all_connections"
]
