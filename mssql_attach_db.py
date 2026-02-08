"""
Script genérico para adjuntar bases de datos MSSQL desde archivos .mdf y .ldf
"""
from paquetes.mssql import get_mssql_connection, execute_query


def attach_database(
    database_name: str,
    mdf_path: str,
    ldf_path: str,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None
) -> bool:
    """
    Adjunta una base de datos a SQL Server desde archivos .mdf y .ldf

    Args:
        database_name: Nombre de la base de datos a crear
        mdf_path: Ruta completa al archivo .mdf
        ldf_path: Ruta completa al archivo .ldf
        host: Host del servidor SQL Server (opcional, lee de MSSQL_HOST)
        port: Puerto del servidor (opcional, lee de MSSQL_PORT)
        user: Usuario de SQL Server (opcional, lee de MSSQL_USER)
        password: Contraseña (opcional, lee de MSSQL_PASSWORD)

    Returns:
        True si la operación fue exitosa, False en caso contrario

    Example:
        # Usando variables de entorno para conexión
        attach_database(
            'progex',
            '/var/opt/mssql/data/progex.mdf',
            '/var/opt/mssql/data/progex_log.ldf'
        )

        # Pasando credenciales directamente
        attach_database(
            'mi_bd',
            '/var/opt/mssql/data/mi_bd.mdf',
            '/var/opt/mssql/data/mi_bd_log.ldf',
            host='localhost',
            port=1433,
            user='sa',
            password='mi_password'
        )
    """
    try:
        print(f"Conectando a SQL Server...")

        # Verificar si la base de datos ya existe
        query = "SELECT name FROM sys.databases WHERE name = ?"
        result = execute_query(query, params=(database_name,), database='master')

        if result:
            print(f"⚠️  La base de datos '{database_name}' ya está adjuntada")
            return True

        print(f"Adjuntando base de datos '{database_name}'...")

        # Para CREATE DATABASE necesitamos autocommit
        conn = get_mssql_connection(
            database='master',
            host=host,
            port=port,
            user=user,
            password=password
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Adjuntar la base de datos
        attach_sql = f"""
        CREATE DATABASE [{database_name}]
        ON (FILENAME = '{mdf_path}'),
           (FILENAME = '{ldf_path}')
        FOR ATTACH
        """

        cursor.execute(attach_sql)
        print(f"✓ Base de datos '{database_name}' adjuntada exitosamente")

        # Verificar
        cursor.execute(
            "SELECT name, state_desc, user_access_desc FROM sys.databases WHERE name = ?",
            (database_name,)
        )
        result = cursor.fetchone()

        if result:
            print(f"✓ Estado: {result[1]}, Acceso: {result[2]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error al adjuntar base de datos '{database_name}': {e}")
        import traceback
        traceback.print_exc()
        return False


def attach_progex(
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None
) -> bool:
    """
    Función de conveniencia para adjuntar la base de datos progex.

    Args:
        host: Host del servidor SQL Server (opcional)
        port: Puerto del servidor (opcional)
        user: Usuario de SQL Server (opcional)
        password: Contraseña (opcional)

    Returns:
        True si la operación fue exitosa, False en caso contrario
    """
    return attach_database(
        database_name='progex',
        mdf_path='/var/opt/mssql/data/progex.mdf',
        ldf_path='/var/opt/mssql/data/progex_log.ldf',
        host=host,
        port=port,
        user=user,
        password=password
    )


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='Adjuntar base de datos SQL Server desde archivos .mdf y .ldf'
    )
    parser.add_argument(
        '--database',
        '-d',
        default='progex',
        help='Nombre de la base de datos (default: progex)'
    )
    parser.add_argument(
        '--mdf',
        help='Ruta al archivo .mdf (default: /var/opt/mssql/data/{database}.mdf)'
    )
    parser.add_argument(
        '--ldf',
        help='Ruta al archivo .ldf (default: /var/opt/mssql/data/{database}_log.ldf)'
    )
    parser.add_argument('--host', help='Host del servidor SQL Server')
    parser.add_argument('--port', type=int, help='Puerto del servidor')
    parser.add_argument('--user', help='Usuario de SQL Server')
    parser.add_argument('--password', help='Contraseña')

    args = parser.parse_args()

    # Usar rutas por defecto si no se especifican
    mdf_path = args.mdf or f'/var/opt/mssql/data/{args.database}.mdf'
    ldf_path = args.ldf or f'/var/opt/mssql/data/{args.database}_log.ldf'

    # Adjuntar base de datos
    success = attach_database(
        database_name=args.database,
        mdf_path=mdf_path,
        ldf_path=ldf_path,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password
    )

    sys.exit(0 if success else 1)
