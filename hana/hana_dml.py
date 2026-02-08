"""
Funciones DML (Data Manipulation Language) para SAP HANA.

Este módulo proporciona funciones para manipular datos en tablas:
SELECT, INSERT, UPDATE, DELETE, y operaciones relacionadas.

⚠️ MÓDULO GENÉRICO: No depende de ningún archivo de configuración específico.
Las credenciales se pasan como parámetros o se leen de variables de entorno.
"""
from hdbcli import dbapi
from typing import Any, Dict, List, Optional, Tuple
import os


def get_hana_connection(
    schema: str | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None
) -> dbapi.Connection:
    """
    Obtiene conexión a SAP HANA.

    Args:
        schema: Nombre del schema (opcional)
        host: Host del servidor HANA (opcional, lee de SAP_HANA_HOST si es None)
        port: Puerto del servidor (opcional, lee de SAP_HANA_PORT si es None)
        user: Usuario de HANA (opcional, lee de SAP_HANA_USER si es None)
        password: Contraseña (opcional, lee de SAP_HANA_PASSWORD si es None)

    Returns:
        Conexión hdbcli activa

    Example:
        # Usando variables de entorno
        conn = get_hana_connection(schema='SBODEMOUY')

        # Pasando credenciales directamente
        conn = get_hana_connection(
            schema='SBODEMOUY',
            host='sap.empresa.local',
            port=30015,
            user='B1ADMIN',
            password='mi_password'
        )
    """
    # Leer de parámetros o variables de entorno
    host = host or os.getenv('SAP_HANA_HOST')
    port = port or int(os.getenv('SAP_HANA_PORT', '30015'))
    user = user or os.getenv('SAP_HANA_USER')
    password = password or os.getenv('SAP_HANA_PASSWORD')

    if not host or not user or not password:
        raise ValueError(
            "Credenciales de SAP HANA no configuradas. "
            "Proporcione los parámetros host, user y password, "
            "o configure las variables de entorno: "
            "SAP_HANA_HOST, SAP_HANA_USER, SAP_HANA_PASSWORD"
        )

    connection = dbapi.connect(
        address=host,
        port=port,
        user=user,
        password=password
    )

    # Establecer schema si se proporciona
    if schema:
        cursor = connection.cursor()
        cursor.execute(f"SET SCHEMA {schema}")
        cursor.close()

    return connection


def insert(
    table: str,
    data: Dict[str, Any],
    schema: str | None = None
) -> int:
    """
    Inserta un registro en una tabla.

    Args:
        table: Nombre de la tabla
        data: Diccionario con columnas y valores {columna: valor}
        schema: Schema opcional

    Returns:
        Número de filas insertadas (normalmente 1)

    Example:
        insert('PRODUCTOS', {
            'CODIGO': 'P001',
            'NOMBRE': 'Producto 1',
            'PRECIO': 100.50
        })
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla y columnas a mayúsculas
        table = table.upper()
        columns = ', '.join([f'"{col.upper()}"' for col in data.keys()])
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())

        query = f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})'
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
    schema: str | None = None,
    batch_size: int = 1000
) -> int:
    """
    Inserta múltiples registros en una tabla por lotes.

    Args:
        table: Nombre de la tabla
        columns: Lista de nombres de columnas
        values_list: Lista de tuplas con valores
        schema: Schema opcional
        batch_size: Tamaño del lote para inserción (default: 1000)

    Returns:
        Total de filas insertadas

    Example:
        insert_many(
            'PRODUCTOS',
            ['CODIGO', 'NOMBRE', 'PRECIO'],
            [
                ('P001', 'Producto 1', 100.50),
                ('P002', 'Producto 2', 200.75),
            ]
        )
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()
    total_inserted = 0

    try:
        # Convertir tabla y columnas a mayúsculas
        table = table.upper()
        columns_str = ', '.join([f'"{col.upper()}"' for col in columns])
        placeholders = ', '.join(['?' for _ in columns])
        query = f'INSERT INTO "{table}" ({columns_str}) VALUES ({placeholders})'

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
    schema: str | None = None
) -> List[Any]:
    """
    Consulta registros de una tabla.

    Args:
        table: Nombre de la tabla
        columns: Lista de columnas a seleccionar (None = todas)
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        order_by: Cláusula ORDER BY (sin las palabras ORDER BY)
        limit: Número máximo de registros
        schema: Schema opcional

    Returns:
        Lista de filas

    Example:
        # Seleccionar todo
        select('PRODUCTOS')

        # Con filtros
        select(
            'PRODUCTOS',
            columns=['CODIGO', 'NOMBRE'],
            where='PRECIO > ?',
            where_params=(100,),
            order_by='NOMBRE'
        )
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla y columnas a mayúsculas
        table = table.upper()

        # Construir columnas
        if columns:
            columns = [col.upper() for col in columns]
            columns_str = ', '.join([f'"{col}"' for col in columns])
        else:
            columns_str = '*'

        # Construir query
        query = f'SELECT {columns_str} FROM "{table}"'

        if where:
            query += f" WHERE {where}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

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
    schema: str | None = None
) -> Any | None:
    """
    Consulta un solo registro de una tabla.

    Args:
        table: Nombre de la tabla
        columns: Lista de columnas a seleccionar (None = todas)
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        schema: Schema opcional

    Returns:
        Primera fila encontrada o None

    Example:
        select_one(
            'PRODUCTOS',
            where='CODIGO = ?',
            where_params=('P001',)
        )
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla y columnas a mayúsculas
        table = table.upper()

        if columns:
            columns = [col.upper() for col in columns]
            columns_str = ', '.join([f'"{col}"' for col in columns])
        else:
            columns_str = '*'

        query = f'SELECT {columns_str} FROM "{table}"'

        if where:
            query += f" WHERE {where}"

        query += " LIMIT 1"

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
    schema: str | None = None
) -> int:
    """
    Actualiza registros en una tabla.

    Args:
        table: Nombre de la tabla
        data: Diccionario con columnas y valores a actualizar {columna: valor}
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        schema: Schema opcional

    Returns:
        Número de filas actualizadas

    Example:
        update(
            'PRODUCTOS',
            {'PRECIO': 150.00, 'NOMBRE': 'Producto Actualizado'},
            where='CODIGO = ?',
            where_params=('P001',)
        )
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla y columnas a mayúsculas
        table = table.upper()
        set_clause = ', '.join([f'"{col.upper()}" = ?' for col in data.keys()])
        values = list(data.values()) + list(where_params)

        query = f'UPDATE "{table}" SET {set_clause} WHERE {where}'
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
    schema: str | None = None
) -> int:
    """
    Elimina registros de una tabla.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        schema: Schema opcional

    Returns:
        Número de filas eliminadas

    Example:
        delete(
            'PRODUCTOS',
            where='CODIGO = ?',
            where_params=('P001',)
        )
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla a mayúsculas
        table = table.upper()

        query = f'DELETE FROM "{table}" WHERE {where}'
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
    schema: str | None = None
) -> bool:
    """
    Verifica si existe al menos un registro que cumpla la condición.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        schema: Schema opcional

    Returns:
        True si existe al menos un registro, False en caso contrario

    Example:
        exists(
            'PRODUCTOS',
            where='CODIGO = ?',
            where_params=('P001',)
        )
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla a mayúsculas
        table = table.upper()

        query = f'SELECT 1 FROM "{table}" WHERE {where} LIMIT 1'
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
    schema: str | None = None
) -> int:
    """
    Cuenta registros en una tabla.

    Args:
        table: Nombre de la tabla
        where: Cláusula WHERE opcional (sin la palabra WHERE)
        where_params: Tupla con parámetros para la cláusula WHERE
        schema: Schema opcional

    Returns:
        Número de registros

    Example:
        # Contar todos
        count('PRODUCTOS')

        # Con filtro
        count('PRODUCTOS', where='PRECIO > ?', where_params=(100,))
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla a mayúsculas
        table = table.upper()

        query = f'SELECT COUNT(*) FROM "{table}"'

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
    schema: str | None = None,
    fetch: bool = True
) -> List[Any] | int:
    """
    Ejecuta una query SQL personalizada.

    Args:
        query: Query SQL completa
        params: Tupla con parámetros para la query
        schema: Schema opcional
        fetch: Si True, retorna resultados. Si False, retorna rowcount

    Returns:
        Lista de filas si fetch=True, número de filas afectadas si fetch=False

    Example:
        # SELECT personalizado
        execute_query(
            "SELECT * FROM PRODUCTOS WHERE PRECIO > ? AND ACTIVO = ?",
            params=(100, 1)
        )

        # UPDATE personalizado
        execute_query(
            "UPDATE PRODUCTOS SET PRECIO = PRECIO * 1.1 WHERE CODIGO LIKE ?",
            params=('P%',),
            fetch=False
        )
    """
    conn = get_hana_connection(schema)
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
    schema: str | None = None
) -> Tuple[int, str]:
    """
    Inserta o actualiza un registro (UPSERT usando REPLACE).

    Args:
        table: Nombre de la tabla
        data: Diccionario con todas las columnas y valores
        key_columns: Lista de columnas que forman la llave primaria
        schema: Schema opcional

    Returns:
        Tupla (rowcount, operation) donde operation es 'inserted' o 'updated'

    Example:
        upsert(
            'PRODUCTOS',
            {
                'CODIGO': 'P001',
                'NOMBRE': 'Producto 1',
                'PRECIO': 100.50
            },
            key_columns=['CODIGO']
        )
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        # Convertir tabla y columnas a mayúsculas
        table = table.upper()
        key_columns = [col.upper() for col in key_columns]

        # Construir condición WHERE para las llaves
        key_condition = ' AND '.join([f'"{col}" = ?' for col in key_columns])
        key_values = tuple([data[col] if col in data else data[col.upper()] for col in key_columns])

        # Verificar si existe
        check_query = f'SELECT 1 FROM "{table}" WHERE {key_condition} LIMIT 1'
        cursor.execute(check_query, key_values)
        exists_record = cursor.fetchone() is not None

        if exists_record:
            # UPDATE - excluir las columnas de la llave del SET
            update_data = {k.upper(): v for k, v in data.items() if k.upper() not in key_columns}
            if update_data:
                set_clause = ', '.join([f'"{col}" = ?' for col in update_data.keys()])
                values = list(update_data.values()) + list(key_values)

                query = f'UPDATE "{table}" SET {set_clause} WHERE {key_condition}'
                cursor.execute(query, values)
                conn.commit()

                return cursor.rowcount, 'updated'
            else:
                return 0, 'updated'
        else:
            # INSERT
            columns = ', '.join([f'"{col.upper()}"' for col in data.keys()])
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())

            query = f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})'
            cursor.execute(query, values)
            conn.commit()

            return cursor.rowcount, 'inserted'
    finally:
        cursor.close()
        conn.close()


def truncate(
    table: str,
    schema: str | None = None
) -> None:
    """
    Vacía completamente una tabla (TRUNCATE).
    ADVERTENCIA: Esta operación no se puede deshacer.

    Args:
        table: Nombre de la tabla
        schema: Schema opcional

    Example:
        truncate('PRODUCTOS_TEMP')
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


def get_table_columns(
    table: str,
    schema: str | None = None
) -> List[Dict[str, Any]]:
    """
    Obtiene información de las columnas de una tabla.

    Args:
        table: Nombre de la tabla (se convierte a mayúsculas automáticamente)
        schema: Schema opcional (se convierte a mayúsculas automáticamente)

    Returns:
        Lista de diccionarios con información de cada columna

    Example:
        columns = get_table_columns('PRODUCTOS')
        for col in columns:
            print(f"{col['name']}: {col['type']} ({col['length']})")

    Note:
        SAP HANA convierte nombres sin comillas a mayúsculas.
        Esta función normaliza los nombres a mayúsculas antes de buscar.
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
