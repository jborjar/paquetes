"""
Funciones DDL (Data Definition Language) para SQL Server.

Este módulo proporciona funciones para crear y modificar la estructura
de bases de datos y tablas en SQL Server.

⚠️ ADVERTENCIA: Las operaciones DDL modifican la estructura de la base de datos
y pueden ser irreversibles. Usar con precaución.
"""
import pyodbc
from typing import List, Dict, Any
from .mssql_dml import get_mssql_connection


def database_exists(database: str) -> bool:
    """
    Verifica si una base de datos existe en SQL Server.

    Args:
        database: Nombre de la base de datos

    Returns:
        True si la base de datos existe, False en caso contrario

    Example:
        if database_exists('API_MCP'):
            print('La base de datos existe')
    """
    conn = get_mssql_connection(database='master')
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM sys.databases WHERE name = ?",
            (database,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_database(database: str, if_not_exists: bool = True) -> bool:
    """
    Crea una base de datos en SQL Server.

    Args:
        database: Nombre de la base de datos a crear
        if_not_exists: Si True, solo crea si no existe (default: True)

    Returns:
        True si se creó la base de datos, False si ya existía (cuando if_not_exists=True)

    Example:
        create_database('MI_BASE_DATOS')
    """
    conn = get_mssql_connection(database='master')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_not_exists and database_exists(database):
            return False

        # Crear base de datos
        cursor.execute(f"CREATE DATABASE [{database}]")
        return True
    finally:
        cursor.close()
        conn.close()


def drop_database(database: str, if_exists: bool = True, force: bool = False) -> bool:
    """
    Elimina una base de datos de SQL Server.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.

    Args:
        database: Nombre de la base de datos a eliminar
        if_exists: Si True, no genera error si no existe (default: True)
        force: Si True, cierra todas las conexiones activas antes de eliminar (default: False)

    Returns:
        True si se eliminó la base de datos, False si no existía (cuando if_exists=True)

    Example:
        drop_database('MI_BASE_DATOS', force=True)
    """
    conn = get_mssql_connection(database='master')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_exists and not database_exists(database):
            return False

        # Forzar cierre de conexiones si se solicita
        if force:
            cursor.execute(f"""
                IF EXISTS (SELECT name FROM sys.databases WHERE name = '{database}')
                BEGIN
                    ALTER DATABASE [{database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                END
            """)

        # Eliminar base de datos
        cursor.execute(f"DROP DATABASE [{database}]")
        return True
    finally:
        cursor.close()
        conn.close()


def recreate_database(database: str) -> bool:
    """
    Elimina y recrea una base de datos desde cero.

    ⚠️ ADVERTENCIA: Esta operación elimina TODOS los datos de la base de datos.

    Args:
        database: Nombre de la base de datos

    Returns:
        True si se completó exitosamente

    Example:
        recreate_database('API_MCP')
    """
    # Eliminar si existe
    drop_database(database, if_exists=True, force=True)

    # Pequeña pausa para asegurar que la BD esté completamente eliminada
    import time
    time.sleep(0.5)

    # Crear nueva
    create_database(database, if_not_exists=False)

    return True


def table_exists(table: str, database: str | None = None) -> bool:
    """
    Verifica si una tabla existe en la base de datos.

    Args:
        table: Nombre de la tabla
        database: Base de datos opcional

    Returns:
        True si la tabla existe, False en caso contrario

    Example:
        if table_exists('SAP_EMPRESAS'):
            print('La tabla existe')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = ?
        """, (table,))

        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_table(
    table: str,
    columns: Dict[str, str],
    primary_key: List[str] | str | None = None,
    if_not_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Crea una tabla en SQL Server.

    Args:
        table: Nombre de la tabla
        columns: Diccionario {nombre_columna: definición_tipo}
        primary_key: Columna(s) que forman la llave primaria (lista o string)
        if_not_exists: Si True, solo crea si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se creó la tabla, False si ya existía (cuando if_not_exists=True)

    Example:
        create_table(
            'MI_TABLA',
            {
                'id': 'INT IDENTITY(1,1)',
                'nombre': 'NVARCHAR(100) NOT NULL',
                'activo': 'BIT DEFAULT 1'
            },
            primary_key='id'
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_not_exists and table_exists(table, database):
            return False

        # Construir definición de columnas
        column_defs = []
        for col_name, col_def in columns.items():
            column_defs.append(f"{col_name} {col_def}")

        # Agregar PRIMARY KEY si se especifica
        if primary_key:
            if isinstance(primary_key, str):
                pk_columns = primary_key
            else:
                pk_columns = ', '.join(primary_key)
            column_defs.append(f"PRIMARY KEY ({pk_columns})")

        # Crear tabla
        columns_sql = ',\n    '.join(column_defs)
        create_sql = f"CREATE TABLE {table} (\n    {columns_sql}\n)"

        cursor.execute(create_sql)
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def drop_table(
    table: str,
    if_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Elimina una tabla de SQL Server.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.

    Args:
        table: Nombre de la tabla
        if_exists: Si True, no genera error si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se eliminó la tabla, False si no existía (cuando if_exists=True)

    Example:
        drop_table('MI_TABLA')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_exists and not table_exists(table, database):
            return False

        # Eliminar tabla
        if if_exists:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        else:
            cursor.execute(f"DROP TABLE {table}")

        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def execute_ddl(
    ddl_statement: str,
    database: str | None = None
) -> None:
    """
    Ejecuta una sentencia DDL (CREATE, ALTER, DROP, etc.).

    Args:
        ddl_statement: Sentencia DDL completa
        database: Base de datos opcional

    Example:
        # Crear tabla con DDL personalizado
        execute_ddl('''
            CREATE TABLE MiTabla (
                id INT IDENTITY(1,1) PRIMARY KEY,
                nombre NVARCHAR(100) NOT NULL,
                fecha DATETIME DEFAULT GETDATE()
            )
        ''')

        # Crear índice
        execute_ddl('CREATE INDEX idx_nombre ON MiTabla(nombre)')

        # Alterar tabla
        execute_ddl('ALTER TABLE MiTabla ADD email NVARCHAR(100)')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute(ddl_statement)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_table_columns(
    table: str,
    database: str | None = None
) -> List[Dict[str, Any]]:
    """
    Obtiene información de las columnas de una tabla.

    Args:
        table: Nombre de la tabla
        database: Base de datos opcional

    Returns:
        Lista de diccionarios con información de cada columna

    Example:
        columns = get_table_columns('SAP_EMPRESAS')
        for col in columns:
            print(f"{col['name']}: {col['type']} ({col['max_length']})")
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                COLUMN_NAME as name,
                DATA_TYPE as type,
                CHARACTER_MAXIMUM_LENGTH as max_length,
                IS_NULLABLE as is_nullable,
                COLUMN_DEFAULT as default_value
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, (table,))

        columns = []
        for row in cursor.fetchall():
            columns.append({
                'name': row.name,
                'type': row.type,
                'max_length': row.max_length,
                'is_nullable': row.is_nullable == 'YES',
                'default_value': row.default_value
            })

        return columns
    finally:
        cursor.close()
        conn.close()


def truncate_table(
    table: str,
    database: str | None = None
) -> None:
    """
    Vacía completamente una tabla (TRUNCATE).

    ⚠️ ADVERTENCIA: Esta operación elimina TODOS los registros y no se puede deshacer.

    Args:
        table: Nombre de la tabla
        database: Base de datos opcional

    Example:
        truncate_table('SAP_PROV_TEMP')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute(f"TRUNCATE TABLE {table}")
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def create_index(
    table: str,
    index_name: str,
    columns: List[str] | str,
    unique: bool = False,
    if_not_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Crea un índice en una tabla.

    Args:
        table: Nombre de la tabla
        index_name: Nombre del índice
        columns: Columna(s) del índice (lista o string)
        unique: Si True, crea índice único (default: False)
        if_not_exists: Si True, solo crea si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se creó el índice, False si ya existía

    Example:
        create_index('SAP_PROVEEDORES', 'idx_cardcode', 'CardCode')
        create_index('SAP_PROVEEDORES', 'idx_inst_card', ['Instancia', 'CardCode'], unique=True)
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_not_exists:
            cursor.execute("""
                SELECT COUNT(*)
                FROM sys.indexes
                WHERE name = ? AND object_id = OBJECT_ID(?)
            """, (index_name, table))

            if cursor.fetchone()[0] > 0:
                return False

        # Construir lista de columnas
        if isinstance(columns, str):
            columns_str = columns
        else:
            columns_str = ', '.join(columns)

        # Construir sentencia CREATE INDEX
        unique_keyword = 'UNIQUE ' if unique else ''
        ddl = f"CREATE {unique_keyword}INDEX {index_name} ON {table}({columns_str})"

        cursor.execute(ddl)
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def drop_index(
    table: str,
    index_name: str,
    if_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Elimina un índice de una tabla.

    Args:
        table: Nombre de la tabla
        index_name: Nombre del índice
        if_exists: Si True, no genera error si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se eliminó el índice, False si no existía

    Example:
        drop_index('SAP_PROVEEDORES', 'idx_cardcode')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_exists:
            cursor.execute("""
                SELECT COUNT(*)
                FROM sys.indexes
                WHERE name = ? AND object_id = OBJECT_ID(?)
            """, (index_name, table))

            if cursor.fetchone()[0] == 0:
                return False

        # Eliminar índice
        cursor.execute(f"DROP INDEX {index_name} ON {table}")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()
