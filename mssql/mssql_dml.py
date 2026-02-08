"""
Funciones DML (Data Manipulation Language) para SQL Server.

Este módulo proporciona funciones para manipular datos en tablas:
SELECT, INSERT, UPDATE, DELETE, y operaciones relacionadas.

⚠️ MÓDULO GENÉRICO: No depende de ningún archivo de configuración específico.
Las credenciales se pasan como parámetros o se leen de variables de entorno.
"""
import pyodbc
import os
from typing import Any, Dict, List, Optional, Tuple


def get_mssql_connection(
    database: str | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None
) -> pyodbc.Connection:
    """
    Obtiene conexión a MSSQL.

    Args:
        database: Nombre de la base de datos (opcional, lee de MSSQL_DATABASE si es None)
        host: Host del servidor (opcional, lee de MSSQL_HOST si es None)
        port: Puerto del servidor (opcional, lee de MSSQL_PORT si es None)
        user: Usuario de SQL Server (opcional, lee de MSSQL_USER si es None)
        password: Contraseña (opcional, lee de MSSQL_PASSWORD si es None)

    Returns:
        Conexión pyodbc activa

    Example:
        # Usando variables de entorno
        conn = get_mssql_connection(database='mi_db')

        # Pasando credenciales directamente
        conn = get_mssql_connection(
            database='mi_db',
            host='localhost',
            port=1433,
            user='sa',
            password='mi_password'
        )
    """
    # Leer de parámetros o variables de entorno
    db = database or os.getenv('MSSQL_DATABASE', 'master')
    host = host or os.getenv('MSSQL_HOST', 'localhost')
    port = port or int(os.getenv('MSSQL_PORT', '1433'))
    user = user or os.getenv('MSSQL_USER', 'sa')
    password = password or os.getenv('MSSQL_PASSWORD', '')

    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={host},{port};"
        f"DATABASE={db};"
        f"UID={user};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)


def insert(
    table: str,
    data: Dict[str, Any],
    database: str | None = None
) -> int:
    """
    Inserta un registro en una tabla.

    Args:
        table: Nombre de la tabla
        data: Diccionario con columnas y valores {columna: valor}
        database: Base de datos opcional

    Returns:
        Número de filas insertadas (normalmente 1)

    Example:
        insert('SAP_EMPRESAS', {
            'Instancia': 'EMPRESA01',
            'SL': 1,
            'Prueba': 0,
            'PrintHeadr': 'Empresa 01'
        })
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()

        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def insert_many(
    table: str,
    columns: List[str],
    values_list: List[Tuple],
    database: str | None = None,
    batch_size: int = 1000
) -> int:
    """
    Inserta múltiples registros en una tabla por lotes.

    Args:
        table: Nombre de la tabla
        columns: Lista de nombres de columnas
        values_list: Lista de tuplas con valores
        database: Base de datos opcional
        batch_size: Tamaño del lote para inserción (default: 1000)

    Returns:
        Total de filas insertadas

    Example:
        insert_many(
            'SAP_PROVEEDORES',
            ['Instancia', 'CardCode', 'CardName'],
            [
                ('EMPRESA01', 'P001', 'Proveedor 1'),
                ('EMPRESA01', 'P002', 'Proveedor 2'),
            ]
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()
    total_inserted = 0

    try:
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

        # Insertar por lotes
        for i in range(0, len(values_list), batch_size):
            batch = values_list[i:i + batch_size]
            cursor.executemany(query, batch)
            conn.commit()
            total_inserted += cursor.rowcount

        return total_inserted
    finally:
        cursor.close()
        conn.close()


def select(
    table: str,
    columns: List[str] | None = None,
    where: str | None = None,
    where_params: Tuple | None = None,
    order_by: str | None = None,
    limit: int | None = None,
    database: str | None = None
) -> List[pyodbc.Row]:
    """
    Consulta registros de una tabla.

    Args:
        table: Nombre de la tabla
        columns: Lista de columnas a seleccionar (None = todas)
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        order_by: Cláusula ORDER BY (sin las palabras ORDER BY)
        limit: Número máximo de registros (TOP en SQL Server)
        database: Base de datos opcional

    Returns:
        Lista de filas (pyodbc.Row)

    Example:
        # Seleccionar todo
        select('SAP_EMPRESAS')

        # Con filtros
        select(
            'SAP_EMPRESAS',
            columns=['Instancia', 'PrintHeadr'],
            where='SL = ?',
            where_params=(1,),
            order_by='Instancia'
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        # Construir columnas
        columns_str = ', '.join(columns) if columns else '*'

        # Construir query
        query = f"SELECT {columns_str} FROM {table}"

        if where:
            query += f" WHERE {where}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            # SQL Server usa TOP en lugar de LIMIT
            query = query.replace(f"SELECT {columns_str}", f"SELECT TOP {limit} {columns_str}")

        # Ejecutar
        if where_params:
            cursor.execute(query, where_params)
        else:
            cursor.execute(query)

        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def select_one(
    table: str,
    columns: List[str] | None = None,
    where: str | None = None,
    where_params: Tuple | None = None,
    database: str | None = None
) -> pyodbc.Row | None:
    """
    Consulta un solo registro de una tabla.

    Args:
        table: Nombre de la tabla
        columns: Lista de columnas a seleccionar (None = todas)
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional

    Returns:
        Primera fila encontrada o None

    Example:
        select_one(
            'SAP_EMPRESAS',
            where='Instancia = ?',
            where_params=('EMPRESA01',)
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        columns_str = ', '.join(columns) if columns else '*'
        query = f"SELECT TOP 1 {columns_str} FROM {table}"

        if where:
            query += f" WHERE {where}"

        if where_params:
            cursor.execute(query, where_params)
        else:
            cursor.execute(query)

        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def update(
    table: str,
    data: Dict[str, Any],
    where: str,
    where_params: Tuple,
    database: str | None = None
) -> int:
    """
    Actualiza registros en una tabla.

    Args:
        table: Nombre de la tabla
        data: Diccionario con columnas y valores a actualizar {columna: valor}
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional

    Returns:
        Número de filas actualizadas

    Example:
        update(
            'SAP_EMPRESAS',
            {'SL': 1, 'PrintHeadr': 'Nueva Empresa'},
            where='Instancia = ?',
            where_params=('EMPRESA01',)
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        values = list(data.values()) + list(where_params)

        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        cursor.execute(query, values)
        conn.commit()

        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def delete(
    table: str,
    where: str,
    where_params: Tuple,
    database: str | None = None
) -> int:
    """
    Elimina registros de una tabla.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional

    Returns:
        Número de filas eliminadas

    Example:
        delete(
            'SAP_EMPRESAS',
            where='Instancia = ?',
            where_params=('EMPRESA01',)
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        query = f"DELETE FROM {table} WHERE {where}"
        cursor.execute(query, where_params)
        conn.commit()

        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def exists(
    table: str,
    where: str,
    where_params: Tuple,
    database: str | None = None
) -> bool:
    """
    Verifica si existe al menos un registro que cumpla la condición.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional

    Returns:
        True si existe al menos un registro, False en caso contrario

    Example:
        exists(
            'SAP_EMPRESAS',
            where='Instancia = ?',
            where_params=('EMPRESA01',)
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        query = f"SELECT TOP 1 1 FROM {table} WHERE {where}"
        cursor.execute(query, where_params)
        result = cursor.fetchone()

        return result is not None
    finally:
        cursor.close()
        conn.close()


def count(
    table: str,
    where: str | None = None,
    where_params: Tuple | None = None,
    database: str | None = None
) -> int:
    """
    Cuenta registros en una tabla.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE opcional (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional

    Returns:
        Número de registros

    Example:
        # Contar todos
        count('SAP_EMPRESAS')

        # Con filtro
        count('SAP_EMPRESAS', where='SL = ?', where_params=(1,))
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        query = f"SELECT COUNT(*) FROM {table}"

        if where:
            query += f" WHERE {where}"

        if where_params:
            cursor.execute(query, where_params)
        else:
            cursor.execute(query)

        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        conn.close()


def execute_query(
    query: str,
    params: Tuple | None = None,
    database: str | None = None,
    fetch: bool = True
) -> List[pyodbc.Row] | int:
    """
    Ejecuta una query SQL personalizada.

    Args:
        query: Query SQL completa
        params: Tupla con parámetros para la query
        database: Base de datos opcional
        fetch: Si True, retorna resultados. Si False, retorna rowcount (para INSERT/UPDATE/DELETE)

    Returns:
        Lista de filas si fetch=True, número de filas afectadas si fetch=False

    Example:
        # SELECT personalizado
        execute_query(
            "SELECT * FROM SAP_EMPRESAS WHERE SL = ? AND Prueba = ?",
            params=(1, 0)
        )

        # UPDATE personalizado
        execute_query(
            "UPDATE SAP_EMPRESAS SET SL = 1 WHERE Instancia LIKE ?",
            params=('EMP%',),
            fetch=False
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def upsert(
    table: str,
    data: Dict[str, Any],
    key_columns: List[str],
    database: str | None = None
) -> Tuple[int, str]:
    """
    Inserta o actualiza un registro (UPSERT/MERGE).

    Args:
        table: Nombre de la tabla
        data: Diccionario con todas las columnas y valores
        key_columns: Lista de columnas que forman la llave primaria
        database: Base de datos opcional

    Returns:
        Tupla (rowcount, operation) donde operation es 'inserted' o 'updated'

    Example:
        upsert(
            'SAP_EMPRESAS',
            {
                'Instancia': 'EMPRESA01',
                'SL': 1,
                'Prueba': 0,
                'PrintHeadr': 'Empresa 01'
            },
            key_columns=['Instancia']
        )
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        # Construir condición WHERE para las llaves
        key_condition = ' AND '.join([f"{col} = ?" for col in key_columns])
        key_values = tuple([data[col] for col in key_columns])

        # Verificar si existe
        check_query = f"SELECT TOP 1 1 FROM {table} WHERE {key_condition}"
        cursor.execute(check_query, key_values)
        exists = cursor.fetchone() is not None

        if exists:
            # UPDATE - excluir las columnas de la llave del SET
            update_data = {k: v for k, v in data.items() if k not in key_columns}
            if update_data:
                set_clause = ', '.join([f"{col} = ?" for col in update_data.keys()])
                values = list(update_data.values()) + list(key_values)

                query = f"UPDATE {table} SET {set_clause} WHERE {key_condition}"
                cursor.execute(query, values)
                conn.commit()

                return cursor.rowcount, 'updated'
            else:
                return 0, 'updated'
        else:
            # INSERT
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())

            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()

            return cursor.rowcount, 'inserted'
    finally:
        cursor.close()
        conn.close()


def table_exists(
    table: str,
    database: str | None = None
) -> bool:
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


def truncate(
    table: str,
    database: str | None = None
) -> None:
    """
    Vacía completamente una tabla (TRUNCATE).
    ADVERTENCIA: Esta operación no se puede deshacer.

    Args:
        table: Nombre de la tabla
        database: Base de datos opcional

    Example:
        truncate('SAP_PROV_ACTIVOS')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute(f"TRUNCATE TABLE {table}")
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
