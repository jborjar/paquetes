"""
Funciones DDL (Data Definition Language) para SAP HANA.

Este módulo proporciona funciones para crear y modificar la estructura
de tablas y schemas en SAP HANA.

⚠️ ADVERTENCIA: Las operaciones DDL modifican la estructura de la base de datos
y pueden ser irreversibles. Usar con precaución.
"""
from hdbcli import dbapi
from typing import List, Dict, Any
from .hana_dml import get_hana_connection


def schema_exists(schema: str) -> bool:
    """
    Verifica si un schema existe en SAP HANA.

    Args:
        schema: Nombre del schema (se convierte a mayúsculas automáticamente)

    Returns:
        True si el schema existe, False en caso contrario

    Example:
        if schema_exists('SBODEMOUY'):
            print('El schema existe')

    Note:
        SAP HANA convierte nombres sin comillas a mayúsculas.
        Esta función normaliza el nombre a mayúsculas antes de buscar.
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        # Convertir a mayúsculas (comportamiento por defecto de HANA)
        schema = schema.upper()

        cursor.execute(
            "SELECT COUNT(*) FROM SYS.SCHEMAS WHERE SCHEMA_NAME = ?",
            (schema,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def get_schemas(
    exclude_system: bool = True,
    exclude_patterns: List[str] | None = None,
    include_patterns: List[str] | None = None,
    exclude_names: List[str] | None = None
) -> List[str]:
    """
    Obtiene lista de schemas en SAP HANA.

    Args:
        exclude_system: Si True, excluye schemas de sistema SAP/HANA (default: True)
        exclude_patterns: Patrones LIKE adicionales a excluir (ej: ['%_PRUEBAS%', '%_TEST%'])
        include_patterns: Patrones LIKE para incluir (ej: ['SBO%'] para solo schemas SAP B1)
        exclude_names: Nombres exactos de schemas a excluir (ej: ['SBOCOMMON', 'SLDDATA'])

    Returns:
        Lista de nombres de schemas ordenados alfabéticamente

    Example:
        # Obtener todos los schemas de usuario (excluye sistema)
        >>> schemas = get_schemas()
        >>> print(schemas)
        ['SBODEMOUY', 'SBOPROD', 'SBOTEST']

        # Obtener solo schemas SAP B1 de producción (excluir pruebas)
        >>> schemas = get_schemas(
        ...     include_patterns=['SBO%'],
        ...     exclude_patterns=['%_PRUEBAS%', '%_TEST%']
        ... )

        # Obtener todos los schemas sin filtros
        >>> all_schemas = get_schemas(exclude_system=False)

        # Excluir schemas específicos
        >>> schemas = get_schemas(
        ...     exclude_names=['SBOCOMMON', 'SLDDATA', 'TEMP_DATA']
        ... )

    Note:
        Los schemas de sistema que se excluyen por defecto incluyen:
        - B1* (SAP Business One internos)
        - _SYS* (HANA sistema)
        - SAP* (SAP sistema)
        - XSSQLCC* (HANA XS)
        - SYS, SYSTEM (sistema)
        - SBOCOMMON (SAP B1 común)
        - HANA_XS_BASE, UIS, COMMON
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        # Construir condiciones WHERE
        where_conditions = []
        params = []

        # Excluir schemas de sistema si se solicita
        if exclude_system:
            system_patterns = [
                "SCHEMA_NAME NOT LIKE 'B1%'",
                "SCHEMA_NAME NOT LIKE '_SYS%'",
                "SCHEMA_NAME NOT LIKE 'SAP%'",
                "SCHEMA_NAME NOT LIKE 'XSSQLCC%'"
            ]
            where_conditions.extend(system_patterns)

            # Schemas específicos de sistema a excluir
            system_names = ['SYS', 'SYSTEM', 'SBOCOMMON', 'SLDDATA', 'HANA_XS_BASE', 'UIS', 'COMMON']
            if exclude_names:
                exclude_names.extend(system_names)
            else:
                exclude_names = system_names

        # Agregar patrones de exclusión personalizados
        if exclude_patterns:
            for pattern in exclude_patterns:
                where_conditions.append("SCHEMA_NAME NOT LIKE ?")
                params.append(pattern)

        # Agregar patrones de inclusión
        if include_patterns:
            include_conditions = []
            for pattern in include_patterns:
                include_conditions.append("SCHEMA_NAME LIKE ?")
                params.append(pattern)
            if include_conditions:
                where_conditions.append(f"({' OR '.join(include_conditions)})")

        # Excluir nombres específicos
        if exclude_names:
            placeholders = ','.join(['?' for _ in exclude_names])
            where_conditions.append(f"SCHEMA_NAME NOT IN ({placeholders})")
            params.extend(exclude_names)

        # Construir query
        query = "SELECT SCHEMA_NAME FROM SYS.SCHEMAS"
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        query += " ORDER BY SCHEMA_NAME"

        # Ejecutar
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Retornar lista de nombres
        return [row[0] for row in cursor.fetchall()]

    finally:
        cursor.close()
        conn.close()


def table_exists(table: str, schema: str | None = None) -> bool:
    """
    Verifica si una tabla existe en el schema.

    Args:
        table: Nombre de la tabla (se convierte a mayúsculas automáticamente)
        schema: Schema opcional (usa el actual si es None)

    Returns:
        True si la tabla existe, False en caso contrario

    Example:
        if table_exists('OITM', schema='SBODEMOUY'):
            print('La tabla existe')

    Note:
        SAP HANA convierte nombres sin comillas a mayúsculas.
        Esta función normaliza el nombre a mayúsculas antes de buscar.
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Obtener el schema actual si no se proporciona
        if not schema:
            cursor.execute("SELECT CURRENT_SCHEMA FROM DUMMY")
            schema = cursor.fetchone()[0]

        # Convertir a mayúsculas (comportamiento por defecto de HANA)
        table = table.upper()
        schema = schema.upper()

        cursor.execute("""
            SELECT COUNT(*)
            FROM SYS.TABLES
            WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
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
    table_type: str = 'ROW',
    if_not_exists: bool = True,
    schema: str | None = None
) -> bool:
    """
    Crea una tabla en SAP HANA.

    Args:
        table: Nombre de la tabla
        columns: Diccionario {nombre_columna: definición_tipo}
        primary_key: Columna(s) que forman la llave primaria (lista o string)
        table_type: Tipo de tabla ('ROW' o 'COLUMN', default: 'ROW')
        if_not_exists: Si True, solo crea si no existe (default: True)
        schema: Schema opcional

    Returns:
        True si se creó la tabla, False si ya existía

    Example:
        create_table(
            'MI_TABLA',
            {
                'ID': 'INTEGER',
                'CODIGO': 'NVARCHAR(50) NOT NULL',
                'NOMBRE': 'NVARCHAR(100)',
                'PRECIO': 'DECIMAL(18,2)',
                'FECHA': 'DATE DEFAULT CURRENT_DATE'
            },
            primary_key='ID',
            table_type='COLUMN'
        )
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla a mayúsculas
        table = table.upper()

        # Verificar si existe
        if if_not_exists and table_exists(table, schema):
            return False

        # Construir definición de columnas (convertir nombres a mayúsculas)
        column_defs = []
        for col_name, col_def in columns.items():
            column_defs.append(f'"{col_name.upper()}" {col_def}')

        # Agregar PRIMARY KEY si se especifica
        if primary_key:
            if isinstance(primary_key, str):
                pk_columns = f'"{primary_key.upper()}"'
            else:
                pk_columns = ', '.join([f'"{col.upper()}"' for col in primary_key])
            column_defs.append(f"PRIMARY KEY ({pk_columns})")

        # Crear tabla
        columns_sql = ',\n    '.join(column_defs)
        create_sql = f'CREATE {table_type} TABLE "{table}" (\n    {columns_sql}\n)'

        cursor.execute(create_sql)
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def drop_table(
    table: str,
    if_exists: bool = True,
    schema: str | None = None
) -> bool:
    """
    Elimina una tabla de SAP HANA.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.

    Args:
        table: Nombre de la tabla (se convierte a mayúsculas automáticamente)
        if_exists: Si True, no genera error si no existe (default: True)
        schema: Schema opcional (se convierte a mayúsculas automáticamente)

    Returns:
        True si se eliminó la tabla, False si no existía

    Example:
        drop_table('MI_TABLA')

    Note:
        SAP HANA convierte nombres sin comillas a mayúsculas.
        Esta función normaliza los nombres a mayúsculas.
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir a mayúsculas (comportamiento por defecto de HANA)
        table = table.upper()

        # Verificar si existe
        if if_exists and not table_exists(table, schema):
            return False

        # Eliminar tabla (usar comillas por seguridad)
        cursor.execute(f'DROP TABLE "{table}"')
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def truncate_table(
    table: str,
    schema: str | None = None
) -> None:
    """
    Vacía completamente una tabla (TRUNCATE).

    ⚠️ ADVERTENCIA: Esta operación elimina TODOS los registros y no se puede deshacer.

    Args:
        table: Nombre de la tabla (se convierte a mayúsculas automáticamente)
        schema: Schema opcional

    Example:
        truncate_table('PRODUCTOS_TEMP')

    Note:
        SAP HANA convierte nombres sin comillas a mayúsculas.
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla a mayúsculas
        table = table.upper()

        cursor.execute(f'TRUNCATE TABLE "{table}"')
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def execute_ddl(
    ddl_statement: str,
    schema: str | None = None
) -> None:
    """
    Ejecuta una sentencia DDL (CREATE, ALTER, DROP, etc.).

    Args:
        ddl_statement: Sentencia DDL completa
        schema: Schema opcional

    Example:
        # Crear tabla con DDL personalizado
        execute_ddl('''
            CREATE COLUMN TABLE MiTabla (
                ID INTEGER PRIMARY KEY,
                NOMBRE NVARCHAR(100) NOT NULL,
                FECHA DATE DEFAULT CURRENT_DATE
            )
        ''')

        # Crear índice
        execute_ddl('CREATE INDEX idx_nombre ON MiTabla(NOMBRE)')

        # Alterar tabla
        execute_ddl('ALTER TABLE MiTabla ADD (EMAIL NVARCHAR(100))')
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        cursor.execute(ddl_statement)
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
    schema: str | None = None
) -> bool:
    """
    Crea un índice en una tabla.

    Args:
        table: Nombre de la tabla
        index_name: Nombre del índice
        columns: Columna(s) del índice (lista o string)
        unique: Si True, crea índice único (default: False)
        if_not_exists: Si True, solo crea si no existe (default: True)
        schema: Schema opcional

    Returns:
        True si se creó el índice, False si ya existía

    Example:
        create_index('PRODUCTOS', 'idx_codigo', 'CODIGO')
        create_index('PRODUCTOS', 'idx_cat_nombre', ['CATEGORIA', 'NOMBRE'], unique=True)
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir a mayúsculas
        table = table.upper()
        index_name = index_name.upper()

        # Verificar si existe
        if if_not_exists:
            if not schema:
                cursor.execute("SELECT CURRENT_SCHEMA FROM DUMMY")
                schema = cursor.fetchone()[0]

            schema = schema.upper()

            cursor.execute("""
                SELECT COUNT(*)
                FROM SYS.INDEXES
                WHERE SCHEMA_NAME = ? AND INDEX_NAME = ?
            """, (schema, index_name))

            if cursor.fetchone()[0] > 0:
                return False

        # Construir lista de columnas
        if isinstance(columns, str):
            columns_str = f'"{columns.upper()}"'
        else:
            columns_str = ', '.join([f'"{col.upper()}"' for col in columns])

        # Construir sentencia CREATE INDEX
        unique_keyword = 'UNIQUE ' if unique else ''
        ddl = f'CREATE {unique_keyword}INDEX "{index_name}" ON "{table}"({columns_str})'

        cursor.execute(ddl)
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def drop_index(
    index_name: str,
    if_exists: bool = True,
    schema: str | None = None
) -> bool:
    """
    Elimina un índice.

    Args:
        index_name: Nombre del índice (se convierte a mayúsculas automáticamente)
        if_exists: Si True, no genera error si no existe (default: True)
        schema: Schema opcional (se convierte a mayúsculas automáticamente)

    Returns:
        True si se eliminó el índice, False si no existía

    Example:
        drop_index('idx_codigo')

    Note:
        SAP HANA convierte nombres sin comillas a mayúsculas.
        Esta función normaliza los nombres a mayúsculas antes de buscar.
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir a mayúsculas (comportamiento por defecto de HANA)
        index_name = index_name.upper()

        # Verificar si existe
        if if_exists:
            if not schema:
                cursor.execute("SELECT CURRENT_SCHEMA FROM DUMMY")
                schema = cursor.fetchone()[0]

            schema = schema.upper()

            cursor.execute("""
                SELECT COUNT(*)
                FROM SYS.INDEXES
                WHERE SCHEMA_NAME = ? AND INDEX_NAME = ?
            """, (schema, index_name))

            if cursor.fetchone()[0] == 0:
                return False

        # Eliminar índice (usar comillas por seguridad)
        cursor.execute(f'DROP INDEX "{index_name}"')
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def get_table_columns(
    table: str,
    schema: str | None = None
) -> List[Dict[str, Any]]:
    """
    Obtiene información de las columnas de una tabla.

    Args:
        table: Nombre de la tabla
        schema: Schema opcional

    Returns:
        Lista de diccionarios con información de cada columna

    Example:
        columns = get_table_columns('OITM', schema='SBODEMOUY')
        for col in columns:
            print(f"{col['name']}: {col['type']} ({col['length']})")
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Obtener el schema actual si no se proporciona
        if not schema:
            cursor.execute("SELECT CURRENT_SCHEMA FROM DUMMY")
            schema = cursor.fetchone()[0]

        cursor.execute("""
            SELECT
                COLUMN_NAME,
                DATA_TYPE_NAME,
                LENGTH,
                SCALE,
                IS_NULLABLE,
                DEFAULT_VALUE,
                POSITION
            FROM SYS.TABLE_COLUMNS
            WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
            ORDER BY POSITION
        """, (schema, table))

        columns = []
        for row in cursor.fetchall():
            columns.append({
                'name': row[0],
                'type': row[1],
                'length': row[2],
                'scale': row[3],
                'is_nullable': row[4] == 'TRUE',
                'default_value': row[5],
                'position': row[6]
            })

        return columns
    finally:
        cursor.close()
        conn.close()
