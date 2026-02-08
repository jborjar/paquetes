"""
Funciones DML (Data Manipulation Language) para PostgreSQL.

Este módulo proporciona funciones para manipular datos en tablas:
SELECT, INSERT, UPDATE, DELETE, y operaciones relacionadas.

⚠️ MÓDULO GENÉRICO: No depende de ningún archivo de configuración específico.
Las credenciales se pasan como parámetros o se leen de variables de entorno.
"""
import psycopg2
import psycopg2.extras
import os
from typing import Any, Dict, List, Optional, Tuple


def get_postgres_connection(
    database: str | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None
) -> psycopg2.extensions.connection:
    """
    Obtiene conexión a PostgreSQL.

    Args:
        database: Nombre de la base de datos (opcional, lee de POSTGRES_DATABASE si es None)
        host: Host del servidor (opcional, lee de POSTGRES_HOST si es None)
        port: Puerto del servidor (opcional, lee de POSTGRES_PORT si es None)
        user: Usuario de PostgreSQL (opcional, lee de POSTGRES_USER si es None)
        password: Contraseña (opcional, lee de POSTGRES_PASSWORD si es None)

    Returns:
        Conexión psycopg2 activa

    Example:
        # Usando variables de entorno
        conn = get_postgres_connection(database='mi_db')

        # Pasando credenciales directamente
        conn = get_postgres_connection(
            database='mi_db',
            host='localhost',
            port=5432,
            user='postgres',
            password='mi_password'
        )
    """
    # Leer de parámetros o variables de entorno
    db = database or os.getenv('POSTGRES_DATABASE', 'postgres')
    host = host or os.getenv('POSTGRES_HOST', 'localhost')
    port = port or int(os.getenv('POSTGRES_PORT', '5432'))
    user = user or os.getenv('POSTGRES_USER', 'postgres')
    password = password or os.getenv('POSTGRES_PASSWORD', '')

    return psycopg2.connect(
        host=host,
        port=port,
        database=db,
        user=user,
        password=password
    )


def insert(
    table: str,
    data: Dict[str, Any],
    database: str | None = None,
    schema: str | None = None,
    returning: str | None = None
) -> Any:
    """
    Inserta un registro en una tabla.

    Args:
        table: Nombre de la tabla
        data: Diccionario con columnas y valores {columna: valor}
        database: Base de datos opcional
        schema: Schema opcional (default: public)
        returning: Columna a retornar (ej: 'id' para obtener el ID insertado)

    Returns:
        Valor de la columna especificada en returning, o número de filas insertadas

    Example:
        # Inserción simple
        insert('empresas', {
            'nombre': 'Empresa 01',
            'activo': True,
            'codigo': 'EMP01'
        })

        # Con RETURNING para obtener ID generado
        nuevo_id = insert('empresas', {
            'nombre': 'Empresa 02'
        }, returning='id')
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()

    try:
        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s' for _ in data])
        values = list(data.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        if returning:
            query += f" RETURNING {returning}"

        cursor.execute(query, values)
        conn.commit()

        if returning:
            result = cursor.fetchone()
            return result[0] if result else None
        else:
            return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def insert_many(
    table: str,
    columns: List[str],
    values_list: List[Tuple],
    database: str | None = None,
    schema: str | None = None,
    batch_size: int = 1000
) -> int:
    """
    Inserta múltiples registros en una tabla por lotes.

    Args:
        table: Nombre de la tabla
        columns: Lista de nombres de columnas
        values_list: Lista de tuplas con valores
        database: Base de datos opcional
        schema: Schema opcional (default: public)
        batch_size: Tamaño del lote para inserción (default: 1000)

    Returns:
        Total de filas insertadas

    Example:
        insert_many(
            'proveedores',
            ['codigo', 'nombre', 'activo'],
            [
                ('P001', 'Proveedor 1', True),
                ('P002', 'Proveedor 2', True),
            ]
        )
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()
    total_inserted = 0

    try:
        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s' for _ in columns])
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

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
    offset: int | None = None,
    database: str | None = None,
    schema: str | None = None
) -> List[Dict[str, Any]]:
    """
    Consulta registros de una tabla.

    Args:
        table: Nombre de la tabla
        columns: Lista de columnas a seleccionar (None = todas)
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        order_by: Cláusula ORDER BY (sin las palabras ORDER BY)
        limit: Número máximo de registros
        offset: Número de registros a saltar
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        Lista de diccionarios con los resultados

    Example:
        # Seleccionar todo
        select('empresas')

        # Con filtros
        select(
            'empresas',
            columns=['nombre', 'activo'],
            where='activo = %s',
            where_params=(True,),
            order_by='nombre',
            limit=10
        )
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        # Construir columnas
        columns_str = ', '.join(columns) if columns else '*'

        # Construir query
        query = f"SELECT {columns_str} FROM {table_name}"

        if where:
            query += f" WHERE {where}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        if offset:
            query += f" OFFSET {offset}"

        # Ejecutar
        if where_params:
            cursor.execute(query, where_params)
        else:
            cursor.execute(query)

        return [dict(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def select_one(
    table: str,
    columns: List[str] | None = None,
    where: str | None = None,
    where_params: Tuple | None = None,
    database: str | None = None,
    schema: str | None = None
) -> Dict[str, Any] | None:
    """
    Consulta un solo registro de una tabla.

    Args:
        table: Nombre de la tabla
        columns: Lista de columnas a seleccionar (None = todas)
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        Diccionario con la primera fila encontrada o None

    Example:
        empresa = select_one(
            'empresas',
            where='codigo = %s',
            where_params=('EMP01',)
        )
    """
    results = select(
        table=table,
        columns=columns,
        where=where,
        where_params=where_params,
        limit=1,
        database=database,
        schema=schema
    )
    return results[0] if results else None


def update(
    table: str,
    data: Dict[str, Any],
    where: str,
    where_params: Tuple,
    database: str | None = None,
    schema: str | None = None
) -> int:
    """
    Actualiza registros en una tabla.

    Args:
        table: Nombre de la tabla
        data: Diccionario con columnas y nuevos valores
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        Número de filas actualizadas

    Example:
        update(
            'empresas',
            {'activo': False},
            where='codigo = %s',
            where_params=('EMP01',)
        )
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()

    try:
        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
        values = list(data.values()) + list(where_params)

        query = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
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
    database: str | None = None,
    schema: str | None = None
) -> int:
    """
    Elimina registros de una tabla.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        Número de filas eliminadas

    Example:
        delete(
            'empresas',
            where='activo = %s AND fecha < %s',
            where_params=(False, '2020-01-01')
        )
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()

    try:
        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        query = f"DELETE FROM {table_name} WHERE {where}"
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
    database: str | None = None,
    schema: str | None = None
) -> bool:
    """
    Verifica si existe al menos un registro que cumpla una condición.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        True si existe, False si no

    Example:
        if exists('empresas', 'codigo = %s', ('EMP01',)):
            print("La empresa existe")
    """
    result = select_one(
        table=table,
        columns=['1'],
        where=where,
        where_params=where_params,
        database=database,
        schema=schema
    )
    return result is not None


def count(
    table: str,
    where: str | None = None,
    where_params: Tuple | None = None,
    database: str | None = None,
    schema: str | None = None
) -> int:
    """
    Cuenta registros en una tabla.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE opcional (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        Número de registros

    Example:
        total = count('empresas')
        activas = count('empresas', 'activo = %s', (True,))
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()

    try:
        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        query = f"SELECT COUNT(*) FROM {table_name}"

        if where:
            query += f" WHERE {where}"

        if where_params:
            cursor.execute(query, where_params)
        else:
            cursor.execute(query)

        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def execute_query(
    query: str,
    params: Tuple | None = None,
    database: str | None = None,
    fetch: bool = True
) -> List[Dict[str, Any]] | int:
    """
    Ejecuta una consulta SQL personalizada.

    Args:
        query: Consulta SQL a ejecutar
        params: Tupla con parámetros para la consulta
        database: Base de datos opcional
        fetch: Si True, retorna resultados; si False, retorna rowcount

    Returns:
        Lista de diccionarios con resultados (si fetch=True) o número de filas afectadas

    Example:
        # Consulta SELECT
        results = execute_query(
            "SELECT * FROM empresas WHERE activo = %s",
            (True,)
        )

        # Consulta UPDATE/DELETE
        affected = execute_query(
            "UPDATE empresas SET activo = %s WHERE codigo = %s",
            (False, 'EMP01'),
            fetch=False
        )
    """
    conn = get_postgres_connection(database)

    if fetch:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cursor = conn.cursor()

    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            return [dict(row) for row in cursor.fetchall()]
        else:
            conn.commit()
            return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def upsert(
    table: str,
    data: Dict[str, Any],
    conflict_columns: List[str],
    update_columns: List[str] | None = None,
    database: str | None = None,
    schema: str | None = None
) -> int:
    """
    Inserta o actualiza un registro (INSERT ... ON CONFLICT).

    Args:
        table: Nombre de la tabla
        data: Diccionario con columnas y valores
        conflict_columns: Columnas que determinan el conflicto
        update_columns: Columnas a actualizar en caso de conflicto (None = todas menos las de conflicto)
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Returns:
        Número de filas afectadas

    Example:
        upsert(
            'empresas',
            {'codigo': 'EMP01', 'nombre': 'Empresa 01', 'activo': True},
            conflict_columns=['codigo'],
            update_columns=['nombre', 'activo']
        )
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()

    try:
        # Preparar schema
        table_name = f"{schema}.{table}" if schema else table

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s' for _ in data])
        values = list(data.values())

        # Determinar columnas a actualizar
        if update_columns is None:
            update_columns = [col for col in data.keys() if col not in conflict_columns]

        update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
        conflict_cols = ', '.join(conflict_columns)

        query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols})
        DO UPDATE SET {update_set}
        """

        cursor.execute(query, values)
        conn.commit()

        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def truncate(
    table: str,
    cascade: bool = False,
    restart_identity: bool = False,
    database: str | None = None,
    schema: str | None = None
) -> None:
    """
    Elimina todos los registros de una tabla (TRUNCATE).

    Args:
        table: Nombre de la tabla
        cascade: Si True, trunca también las tablas dependientes
        restart_identity: Si True, reinicia las secuencias de identidad
        database: Base de datos opcional
        schema: Schema opcional (default: public)

    Example:
        truncate('logs', restart_identity=True)
    """
    conn = get_postgres_connection(database)
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
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_table_columns(
    table: str,
    database: str | None = None,
    schema: str = 'public'
) -> List[Dict[str, Any]]:
    """
    Obtiene información de las columnas de una tabla.

    Args:
        table: Nombre de la tabla
        database: Base de datos opcional
        schema: Schema de la tabla (default: public)

    Returns:
        Lista de diccionarios con información de columnas

    Example:
        columns = get_table_columns('empresas')
        for col in columns:
            print(f"{col['column_name']}: {col['data_type']}")
    """
    query = """
    SELECT
        column_name,
        data_type,
        character_maximum_length,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_schema = %s AND table_name = %s
    ORDER BY ordinal_position
    """

    return execute_query(query, (schema, table), database=database)
