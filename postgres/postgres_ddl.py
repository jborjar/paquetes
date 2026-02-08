"""
Funciones DDL (Data Definition Language) para PostgreSQL.

Este módulo proporciona funciones para crear y modificar la estructura
de bases de datos, schemas y tablas en PostgreSQL.

⚠️ ADVERTENCIA: Las operaciones DDL modifican la estructura de la base de datos
y pueden ser irreversibles. Usar con precaución.
"""
import psycopg2
from typing import List, Dict, Any
from .postgres_dml import get_postgres_connection


def database_exists(database: str, host: str | None = None) -> bool:
    """
    Verifica si una base de datos existe en PostgreSQL.

    Args:
        database: Nombre de la base de datos
        host: Host del servidor (opcional)

    Returns:
        True si la base de datos existe, False en caso contrario

    Example:
        if database_exists('mi_base'):
            print('La base de datos existe')
    """
    conn = get_postgres_connection(database='postgres', host=host)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM pg_database WHERE datname = %s",
            (database,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_database(
    database: str,
    owner: str | None = None,
    encoding: str = 'UTF8',
    if_not_exists: bool = True
) -> bool:
    """
    Crea una base de datos en PostgreSQL.

    Args:
        database: Nombre de la base de datos a crear
        owner: Usuario propietario de la base de datos (opcional)
        encoding: Encoding de la base de datos (default: UTF8)
        if_not_exists: Si True, solo crea si no existe (default: True)

    Returns:
        True si se creó la base de datos, False si ya existía (cuando if_not_exists=True)

    Example:
        create_database('mi_base', owner='mi_usuario')
    """
    # Conectar a postgres (base de datos administrativa)
    conn = get_postgres_connection(database='postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_not_exists and database_exists(database):
            return False

        # Construir query
        query = f"CREATE DATABASE {database}"

        if owner:
            query += f" OWNER {owner}"

        query += f" ENCODING '{encoding}'"

        cursor.execute(query)
        return True
    finally:
        cursor.close()
        conn.close()


def drop_database(
    database: str,
    if_exists: bool = True,
    force: bool = False
) -> bool:
    """
    Elimina una base de datos de PostgreSQL.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.

    Args:
        database: Nombre de la base de datos a eliminar
        if_exists: Si True, no genera error si no existe (default: True)
        force: Si True, cierra todas las conexiones activas antes de eliminar (default: False)

    Returns:
        True si se eliminó la base de datos, False si no existía (cuando if_exists=True)

    Example:
        drop_database('mi_base', force=True)
    """
    conn = get_postgres_connection(database='postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_exists and not database_exists(database):
            return False

        # Forzar cierre de conexiones si se solicita (PostgreSQL 13+)
        if force:
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid()
            """, (database,))

        # Eliminar base de datos
        cursor.execute(f"DROP DATABASE {database}")
        return True
    finally:
        cursor.close()
        conn.close()


def recreate_database(database: str, owner: str | None = None) -> bool:
    """
    Elimina y recrea una base de datos desde cero.

    ⚠️ ADVERTENCIA: Esta operación elimina TODOS los datos de la base de datos.

    Args:
        database: Nombre de la base de datos
        owner: Usuario propietario (opcional)

    Returns:
        True si se completó exitosamente

    Example:
        recreate_database('mi_base')
    """
    # Eliminar si existe
    drop_database(database, if_exists=True, force=True)

    # Pequeña pausa para asegurar que la BD esté completamente eliminada
    import time
    time.sleep(0.5)

    # Crear nueva
    create_database(database, owner=owner, if_not_exists=False)

    return True


def schema_exists(
    schema: str,
    database: str | None = None
) -> bool:
    """
    Verifica si un schema existe en PostgreSQL.

    Args:
        schema: Nombre del schema
        database: Base de datos opcional

    Returns:
        True si el schema existe, False en caso contrario

    Example:
        if schema_exists('mi_schema'):
            print('El schema existe')
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = %s",
            (schema,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_schema(
    schema: str,
    authorization: str | None = None,
    if_not_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Crea un schema en PostgreSQL.

    Args:
        schema: Nombre del schema
        authorization: Usuario propietario del schema (opcional)
        if_not_exists: Si True, solo crea si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se creó el schema, False si ya existía (cuando if_not_exists=True)

    Example:
        create_schema('ventas', authorization='app_user')
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_not_exists and schema_exists(schema, database):
            return False

        # Construir query
        query = f"CREATE SCHEMA {schema}"

        if authorization:
            query += f" AUTHORIZATION {authorization}"

        cursor.execute(query)
        return True
    finally:
        cursor.close()
        conn.close()


def drop_schema(
    schema: str,
    if_exists: bool = True,
    cascade: bool = False,
    database: str | None = None
) -> bool:
    """
    Elimina un schema de PostgreSQL.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.

    Args:
        schema: Nombre del schema a eliminar
        if_exists: Si True, no genera error si no existe (default: True)
        cascade: Si True, elimina también todos los objetos contenidos (default: False)
        database: Base de datos opcional

    Returns:
        True si se eliminó el schema, False si no existía (cuando if_exists=True)

    Example:
        drop_schema('ventas', cascade=True)
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_exists and not schema_exists(schema, database):
            return False

        # Construir query
        query = f"DROP SCHEMA {schema}"

        if cascade:
            query += " CASCADE"

        cursor.execute(query)
        return True
    finally:
        cursor.close()
        conn.close()


def table_exists(
    table: str,
    database: str | None = None,
    schema: str = 'public'
) -> bool:
    """
    Verifica si una tabla existe en la base de datos.

    Args:
        table: Nombre de la tabla
        database: Base de datos opcional
        schema: Schema de la tabla (default: public)

    Returns:
        True si la tabla existe, False en caso contrario

    Example:
        if table_exists('empresas', schema='ventas'):
            print('La tabla existe')
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
        """, (schema, table))

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
    database: str | None = None,
    schema: str | None = None
) -> bool:
    """
    Crea una tabla en PostgreSQL.

    Args:
        table: Nombre de la tabla
        columns: Diccionario {nombre_columna: definición_tipo}
        primary_key: Columna(s) que forman la llave primaria (lista o string)
        if_not_exists: Si True, solo crea si no existe (default: True)
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        True si se creó la tabla, False si ya existía (cuando if_not_exists=True)

    Example:
        create_table(
            'empresas',
            {
                'id': 'SERIAL',
                'codigo': 'VARCHAR(50) UNIQUE NOT NULL',
                'nombre': 'VARCHAR(200) NOT NULL',
                'activo': 'BOOLEAN DEFAULT TRUE',
                'fecha_registro': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            primary_key='id'
        )
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_not_exists and table_exists(table, database, schema or 'public'):
            return False

        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        # Construir columnas
        columns_def = []
        for col_name, col_type in columns.items():
            columns_def.append(f"{col_name} {col_type}")

        # Agregar primary key si se especifica
        if primary_key:
            if isinstance(primary_key, str):
                pk_cols = primary_key
            else:
                pk_cols = ', '.join(primary_key)
            columns_def.append(f"PRIMARY KEY ({pk_cols})")

        columns_str = ',\n    '.join(columns_def)

        query = f"CREATE TABLE {table_name} (\n    {columns_str}\n)"
        cursor.execute(query)
        return True
    finally:
        cursor.close()
        conn.close()


def drop_table(
    table: str,
    if_exists: bool = True,
    cascade: bool = False,
    database: str | None = None,
    schema: str | None = None
) -> bool:
    """
    Elimina una tabla de PostgreSQL.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.

    Args:
        table: Nombre de la tabla
        if_exists: Si True, no genera error si no existe (default: True)
        cascade: Si True, elimina también objetos dependientes (default: False)
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        True si se eliminó la tabla, False si no existía (cuando if_exists=True)

    Example:
        drop_table('logs', cascade=True)
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_exists and not table_exists(table, database, schema or 'public'):
            return False

        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        query = f"DROP TABLE {table_name}"

        if cascade:
            query += " CASCADE"

        cursor.execute(query)
        return True
    finally:
        cursor.close()
        conn.close()


def truncate_table(
    table: str,
    restart_identity: bool = False,
    cascade: bool = False,
    database: str | None = None,
    schema: str | None = None
) -> None:
    """
    Elimina todos los registros de una tabla (TRUNCATE).

    Args:
        table: Nombre de la tabla
        restart_identity: Si True, reinicia las secuencias (default: False)
        cascade: Si True, trunca también tablas referenciadas (default: False)
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Example:
        truncate_table('logs', restart_identity=True)
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        query = f"TRUNCATE TABLE {table_name}"

        if restart_identity:
            query += " RESTART IDENTITY"

        if cascade:
            query += " CASCADE"

        cursor.execute(query)
    finally:
        cursor.close()
        conn.close()


def execute_ddl(
    ddl: str,
    database: str | None = None
) -> None:
    """
    Ejecuta una sentencia DDL personalizada.

    Args:
        ddl: Sentencia DDL a ejecutar
        database: Base de datos opcional

    Example:
        execute_ddl("ALTER TABLE empresas ADD COLUMN telefono VARCHAR(20)")
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(ddl)
    finally:
        cursor.close()
        conn.close()


def create_index(
    index_name: str,
    table: str,
    columns: List[str] | str,
    unique: bool = False,
    if_not_exists: bool = True,
    method: str | None = None,
    database: str | None = None,
    schema: str | None = None
) -> bool:
    """
    Crea un índice en una tabla.

    Args:
        index_name: Nombre del índice
        table: Nombre de la tabla
        columns: Columna(s) a indexar (lista o string)
        unique: Si True, crea un índice único (default: False)
        if_not_exists: Si True, solo crea si no existe (default: True)
        method: Método del índice: btree, hash, gist, gin, etc. (default: btree)
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        True si se creó el índice, False si ya existía (cuando if_not_exists=True)

    Example:
        create_index('idx_empresas_codigo', 'empresas', 'codigo', unique=True)
        create_index('idx_empresas_nombre', 'empresas', ['nombre', 'activo'])
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_not_exists:
            cursor.execute(
                "SELECT COUNT(*) FROM pg_indexes WHERE indexname = %s",
                (index_name,)
            )
            if cursor.fetchone()[0] > 0:
                return False

        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        # Preparar columnas
        if isinstance(columns, str):
            cols_str = columns
        else:
            cols_str = ', '.join(columns)

        # Construir query
        query = "CREATE "
        if unique:
            query += "UNIQUE "
        query += f"INDEX {index_name} ON {table_name}"

        if method:
            query += f" USING {method}"

        query += f" ({cols_str})"

        cursor.execute(query)
        return True
    finally:
        cursor.close()
        conn.close()


def drop_index(
    index_name: str,
    if_exists: bool = True,
    cascade: bool = False,
    database: str | None = None,
    schema: str | None = None
) -> bool:
    """
    Elimina un índice.

    Args:
        index_name: Nombre del índice
        if_exists: Si True, no genera error si no existe (default: True)
        cascade: Si True, elimina objetos dependientes (default: False)
        database: Base de datos opcional
        schema: Schema opcional

    Returns:
        True si se eliminó el índice, False si no existía (cuando if_exists=True)

    Example:
        drop_index('idx_empresas_codigo')
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verificar si existe
        if if_exists:
            query_check = "SELECT COUNT(*) FROM pg_indexes WHERE indexname = %s"
            if schema:
                query_check += " AND schemaname = %s"
                cursor.execute(query_check, (index_name, schema))
            else:
                cursor.execute(query_check, (index_name,))

            if cursor.fetchone()[0] == 0:
                return False

        # Preparar schema
        index_full_name = f"{schema}.{index_name}" if schema else index_name

        query = f"DROP INDEX {index_full_name}"

        if cascade:
            query += " CASCADE"

        cursor.execute(query)
        return True
    finally:
        cursor.close()
        conn.close()
