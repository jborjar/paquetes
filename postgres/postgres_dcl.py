"""
Funciones DCL (Data Control Language) para PostgreSQL.

Este módulo proporciona funciones para control de acceso y permisos:
- Gestión de roles y usuarios
- Gestión de permisos (GRANT, REVOKE)
- Gestión de privilegios

⚠️ ADVERTENCIA: Las operaciones DCL modifican permisos y seguridad.
Solo deben ser ejecutadas por administradores de base de datos.

Nota: En PostgreSQL, usuarios y roles son equivalentes. Un usuario es un
rol con privilegio LOGIN.
"""
import psycopg2
from typing import List, Dict, Any
from .postgres_dml import get_postgres_connection


# ============================================================================
# GESTIÓN DE ROLES Y USUARIOS
# ============================================================================

def role_exists(role_name: str, database: str | None = None) -> bool:
    """
    Verifica si un rol existe en PostgreSQL.

    Args:
        role_name: Nombre del rol
        database: Base de datos opcional (los roles son globales, pero necesita conexión)

    Returns:
        True si el rol existe, False en caso contrario

    Example:
        if role_exists('app_user'):
            print('El rol existe')
    """
    conn = get_postgres_connection(database or 'postgres')
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM pg_roles WHERE rolname = %s",
            (role_name,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_role(
    role_name: str,
    password: str | None = None,
    login: bool = True,
    superuser: bool = False,
    createdb: bool = False,
    createrole: bool = False,
    if_not_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Crea un rol en PostgreSQL.

    Args:
        role_name: Nombre del rol
        password: Contraseña del rol (opcional)
        login: Si True, permite login (crea un usuario) (default: True)
        superuser: Si True, otorga privilegios de superusuario (default: False)
        createdb: Si True, permite crear bases de datos (default: False)
        createrole: Si True, permite crear roles (default: False)
        if_not_exists: Si True, solo crea si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se creó el rol, False si ya existía

    Example:
        # Crear usuario normal
        create_role('app_user', 'P@ssw0rd!123')

        # Crear rol sin login
        create_role('read_only', login=False)

        # Crear usuario con privilegios
        create_role('admin_user', 'Admin123!', createdb=True, createrole=True)
    """
    conn = get_postgres_connection(database or 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if if_not_exists and role_exists(role_name, database):
            return False

        # Construir query
        query = f"CREATE ROLE {role_name}"

        options = []
        if login:
            options.append("LOGIN")
        if superuser:
            options.append("SUPERUSER")
        if createdb:
            options.append("CREATEDB")
        if createrole:
            options.append("CREATEROLE")
        if password:
            options.append(f"PASSWORD '{password}'")

        if options:
            query += " WITH " + " ".join(options)

        cursor.execute(query)
        return True
    finally:
        cursor.close()
        conn.close()


def create_user(
    username: str,
    password: str,
    createdb: bool = False,
    createrole: bool = False,
    if_not_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Crea un usuario en PostgreSQL (alias conveniente para create_role con LOGIN).

    Args:
        username: Nombre del usuario
        password: Contraseña del usuario
        createdb: Si True, permite crear bases de datos (default: False)
        createrole: Si True, permite crear roles (default: False)
        if_not_exists: Si True, solo crea si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se creó el usuario, False si ya existía

    Example:
        create_user('app_user', 'P@ssw0rd!123')
    """
    return create_role(
        role_name=username,
        password=password,
        login=True,
        createdb=createdb,
        createrole=createrole,
        if_not_exists=if_not_exists,
        database=database
    )


def drop_role(
    role_name: str,
    if_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Elimina un rol de PostgreSQL.

    Args:
        role_name: Nombre del rol
        if_exists: Si True, no genera error si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se eliminó el rol, False si no existía

    Example:
        drop_role('app_user')
    """
    conn = get_postgres_connection(database or 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if if_exists and not role_exists(role_name, database):
            return False

        cursor.execute(f"DROP ROLE {role_name}")
        return True
    finally:
        cursor.close()
        conn.close()


def drop_user(username: str, if_exists: bool = True, database: str | None = None) -> bool:
    """
    Elimina un usuario de PostgreSQL (alias para drop_role).

    Args:
        username: Nombre del usuario
        if_exists: Si True, no genera error si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se eliminó el usuario, False si no existía

    Example:
        drop_user('app_user')
    """
    return drop_role(role_name=username, if_exists=if_exists, database=database)


def alter_role_password(
    role_name: str,
    new_password: str,
    database: str | None = None
) -> None:
    """
    Cambia la contraseña de un rol.

    Args:
        role_name: Nombre del rol
        new_password: Nueva contraseña
        database: Base de datos opcional

    Example:
        alter_role_password('app_user', 'NewP@ssw0rd!456')
    """
    conn = get_postgres_connection(database or 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f"ALTER ROLE {role_name} WITH PASSWORD '{new_password}'")
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# GESTIÓN DE PERMISOS
# ============================================================================

def grant_database_privileges(
    role_name: str,
    database: str,
    privileges: List[str] | str = 'ALL',
    admin_database: str | None = None
) -> None:
    """
    Otorga privilegios sobre una base de datos a un rol.

    Args:
        role_name: Nombre del rol
        database: Base de datos sobre la que otorgar privilegios
        privileges: Privilegios a otorgar (ALL, CONNECT, CREATE, TEMPORARY, TEMP)
        admin_database: Base de datos administrativa para conectarse (default: postgres)

    Example:
        grant_database_privileges('app_user', 'mi_base', 'ALL')
        grant_database_privileges('app_user', 'mi_base', ['CONNECT', 'CREATE'])
    """
    conn = get_postgres_connection(admin_database or 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if isinstance(privileges, list):
            privs = ', '.join(privileges)
        else:
            privs = privileges

        cursor.execute(f"GRANT {privs} ON DATABASE {database} TO {role_name}")
    finally:
        cursor.close()
        conn.close()


def revoke_database_privileges(
    role_name: str,
    database: str,
    privileges: List[str] | str = 'ALL',
    admin_database: str | None = None
) -> None:
    """
    Revoca privilegios sobre una base de datos a un rol.

    Args:
        role_name: Nombre del rol
        database: Base de datos sobre la que revocar privilegios
        privileges: Privilegios a revocar (ALL, CONNECT, CREATE, TEMPORARY, TEMP)
        admin_database: Base de datos administrativa para conectarse (default: postgres)

    Example:
        revoke_database_privileges('app_user', 'mi_base', 'CREATE')
    """
    conn = get_postgres_connection(admin_database or 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if isinstance(privileges, list):
            privs = ', '.join(privileges)
        else:
            privs = privileges

        cursor.execute(f"REVOKE {privs} ON DATABASE {database} FROM {role_name}")
    finally:
        cursor.close()
        conn.close()


def grant_schema_privileges(
    role_name: str,
    schema: str,
    privileges: List[str] | str = 'ALL',
    database: str | None = None
) -> None:
    """
    Otorga privilegios sobre un schema a un rol.

    Args:
        role_name: Nombre del rol
        schema: Schema sobre el que otorgar privilegios
        privileges: Privilegios a otorgar (ALL, CREATE, USAGE)
        database: Base de datos donde está el schema

    Example:
        grant_schema_privileges('app_user', 'public', 'ALL')
        grant_schema_privileges('app_user', 'ventas', ['CREATE', 'USAGE'])
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if isinstance(privileges, list):
            privs = ', '.join(privileges)
        else:
            privs = privileges

        cursor.execute(f"GRANT {privs} ON SCHEMA {schema} TO {role_name}")
    finally:
        cursor.close()
        conn.close()


def revoke_schema_privileges(
    role_name: str,
    schema: str,
    privileges: List[str] | str = 'ALL',
    database: str | None = None
) -> None:
    """
    Revoca privilegios sobre un schema a un rol.

    Args:
        role_name: Nombre del rol
        schema: Schema sobre el que revocar privilegios
        privileges: Privilegios a revocar (ALL, CREATE, USAGE)
        database: Base de datos donde está el schema

    Example:
        revoke_schema_privileges('app_user', 'ventas', 'CREATE')
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if isinstance(privileges, list):
            privs = ', '.join(privileges)
        else:
            privs = privileges

        cursor.execute(f"REVOKE {privs} ON SCHEMA {schema} FROM {role_name}")
    finally:
        cursor.close()
        conn.close()


def grant_table_privileges(
    role_name: str,
    table: str,
    privileges: List[str] | str = 'ALL',
    schema: str = 'public',
    database: str | None = None
) -> None:
    """
    Otorga privilegios sobre una tabla a un rol.

    Args:
        role_name: Nombre del rol
        table: Nombre de la tabla
        privileges: Privilegios a otorgar (ALL, SELECT, INSERT, UPDATE, DELETE, etc.)
        schema: Schema de la tabla (default: public)
        database: Base de datos opcional

    Example:
        grant_table_privileges('app_user', 'empresas', 'ALL')
        grant_table_privileges('app_user', 'empresas', ['SELECT', 'INSERT'])
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        table_name = f"{schema}.{table}" if schema else table

        if isinstance(privileges, list):
            privs = ', '.join(privileges)
        else:
            privs = privileges

        cursor.execute(f"GRANT {privs} ON TABLE {table_name} TO {role_name}")
    finally:
        cursor.close()
        conn.close()


def revoke_table_privileges(
    role_name: str,
    table: str,
    privileges: List[str] | str = 'ALL',
    schema: str = 'public',
    database: str | None = None
) -> None:
    """
    Revoca privilegios sobre una tabla a un rol.

    Args:
        role_name: Nombre del rol
        table: Nombre de la tabla
        privileges: Privilegios a revocar (ALL, SELECT, INSERT, UPDATE, DELETE, etc.)
        schema: Schema de la tabla (default: public)
        database: Base de datos opcional

    Example:
        revoke_table_privileges('app_user', 'empresas', 'DELETE')
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        table_name = f"{schema}.{table}" if schema else table

        if isinstance(privileges, list):
            privs = ', '.join(privileges)
        else:
            privs = privileges

        cursor.execute(f"REVOKE {privs} ON TABLE {table_name} FROM {role_name}")
    finally:
        cursor.close()
        conn.close()


def grant_all_tables_in_schema(
    role_name: str,
    schema: str,
    privileges: List[str] | str = 'ALL',
    database: str | None = None
) -> None:
    """
    Otorga privilegios sobre todas las tablas de un schema a un rol.

    Args:
        role_name: Nombre del rol
        schema: Schema con las tablas
        privileges: Privilegios a otorgar (ALL, SELECT, INSERT, UPDATE, DELETE, etc.)
        database: Base de datos opcional

    Example:
        grant_all_tables_in_schema('app_user', 'public', 'ALL')
        grant_all_tables_in_schema('readonly', 'ventas', 'SELECT')
    """
    conn = get_postgres_connection(database)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if isinstance(privileges, list):
            privs = ', '.join(privileges)
        else:
            privs = privileges

        cursor.execute(f"GRANT {privs} ON ALL TABLES IN SCHEMA {schema} TO {role_name}")
    finally:
        cursor.close()
        conn.close()


def grant_role_to_user(
    role_name: str,
    user_name: str,
    database: str | None = None
) -> None:
    """
    Otorga un rol a un usuario.

    Args:
        role_name: Nombre del rol a otorgar
        user_name: Nombre del usuario que recibirá el rol
        database: Base de datos opcional

    Example:
        grant_role_to_user('read_only', 'app_user')
    """
    conn = get_postgres_connection(database or 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f"GRANT {role_name} TO {user_name}")
    finally:
        cursor.close()
        conn.close()


def revoke_role_from_user(
    role_name: str,
    user_name: str,
    database: str | None = None
) -> None:
    """
    Revoca un rol de un usuario.

    Args:
        role_name: Nombre del rol a revocar
        user_name: Nombre del usuario
        database: Base de datos opcional

    Example:
        revoke_role_from_user('read_only', 'app_user')
    """
    conn = get_postgres_connection(database or 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f"REVOKE {role_name} FROM {user_name}")
    finally:
        cursor.close()
        conn.close()


def get_role_privileges(
    role_name: str,
    database: str | None = None
) -> List[Dict[str, Any]]:
    """
    Obtiene los privilegios de un rol sobre tablas.

    Args:
        role_name: Nombre del rol
        database: Base de datos opcional

    Returns:
        Lista de diccionarios con información de privilegios

    Example:
        privileges = get_role_privileges('app_user')
        for priv in privileges:
            print(f"{priv['table_schema']}.{priv['table_name']}: {priv['privilege_type']}")
    """
    conn = get_postgres_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                table_schema,
                table_name,
                privilege_type
            FROM information_schema.table_privileges
            WHERE grantee = %s
            ORDER BY table_schema, table_name, privilege_type
        """, (role_name,))

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def get_user_roles(
    username: str,
    database: str | None = None
) -> List[str]:
    """
    Obtiene los roles asignados a un usuario.

    Args:
        username: Nombre del usuario
        database: Base de datos opcional

    Returns:
        Lista de nombres de roles

    Example:
        roles = get_user_roles('app_user')
        print(f"Roles: {', '.join(roles)}")
    """
    conn = get_postgres_connection(database or 'postgres')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT r.rolname
            FROM pg_roles r
            JOIN pg_auth_members am ON r.oid = am.roleid
            JOIN pg_roles m ON am.member = m.oid
            WHERE m.rolname = %s
            ORDER BY r.rolname
        """, (username,))

        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# UTILIDADES DE SEGURIDAD
# ============================================================================

def create_readonly_user(
    username: str,
    password: str,
    database: str,
    schema: str = 'public'
) -> None:
    """
    Crea un usuario con permisos de solo lectura en un schema.

    Args:
        username: Nombre del usuario
        password: Contraseña del usuario
        database: Base de datos
        schema: Schema (default: public)

    Example:
        create_readonly_user('readonly', 'Pass123!', 'mi_base')
    """
    # Crear usuario
    create_user(username, password, database='postgres')

    # Otorgar CONNECT a la base de datos
    grant_database_privileges(username, database, 'CONNECT', admin_database='postgres')

    # Otorgar USAGE en el schema
    grant_schema_privileges(username, schema, 'USAGE', database=database)

    # Otorgar SELECT en todas las tablas
    grant_all_tables_in_schema(username, schema, 'SELECT', database=database)


def create_readwrite_user(
    username: str,
    password: str,
    database: str,
    schema: str = 'public'
) -> None:
    """
    Crea un usuario con permisos de lectura y escritura en un schema.

    Args:
        username: Nombre del usuario
        password: Contraseña del usuario
        database: Base de datos
        schema: Schema (default: public)

    Example:
        create_readwrite_user('app_user', 'Pass123!', 'mi_base')
    """
    # Crear usuario
    create_user(username, password, database='postgres')

    # Otorgar CONNECT a la base de datos
    grant_database_privileges(username, database, 'CONNECT', admin_database='postgres')

    # Otorgar ALL en el schema
    grant_schema_privileges(username, schema, 'ALL', database=database)

    # Otorgar ALL en todas las tablas
    grant_all_tables_in_schema(username, schema, 'ALL', database=database)


# ============================================================================
# GESTIÓN DE CONEXIONES
# ============================================================================

def get_active_connections(database: str | None = None) -> List[Dict[str, Any]]:
    """
    Obtiene las conexiones activas en PostgreSQL.

    Args:
        database: Base de datos opcional (None = todas)

    Returns:
        Lista de diccionarios con información de conexiones

    Example:
        connections = get_active_connections()
        for conn in connections:
            print(f"{conn['usename']}@{conn['datname']}: {conn['state']}")
    """
    conn = get_postgres_connection(database or 'postgres')
    cursor = conn.cursor()

    try:
        query = """
            SELECT
                pid,
                usename,
                datname,
                client_addr,
                state,
                query,
                backend_start,
                state_change
            FROM pg_stat_activity
            WHERE pid <> pg_backend_pid()
        """

        if database:
            query += " AND datname = %s"
            cursor.execute(query, (database,))
        else:
            cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def get_connection_count(database: str | None = None) -> int:
    """
    Obtiene el número de conexiones activas.

    Args:
        database: Base de datos opcional (None = todas)

    Returns:
        Número de conexiones activas

    Example:
        count = get_connection_count('mi_base')
        print(f"Conexiones activas: {count}")
    """
    return len(get_active_connections(database))


def terminate_connection(pid: int, database: str | None = None) -> bool:
    """
    Termina una conexión específica.

    Args:
        pid: Process ID de la conexión
        database: Base de datos opcional

    Returns:
        True si se terminó la conexión exitosamente

    Example:
        terminate_connection(12345)
    """
    conn = get_postgres_connection(database or 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT pg_terminate_backend(%s)", (pid,))
        result = cursor.fetchone()
        return result[0] if result else False
    finally:
        cursor.close()
        conn.close()


def terminate_all_connections(
    database: str,
    exclude_current: bool = True
) -> int:
    """
    Termina todas las conexiones a una base de datos.

    Args:
        database: Base de datos
        exclude_current: Si True, excluye la conexión actual (default: True)

    Returns:
        Número de conexiones terminadas

    Example:
        count = terminate_all_connections('mi_base')
        print(f"Conexiones terminadas: {count}")
    """
    conn = get_postgres_connection('postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        query = """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s
        """

        if exclude_current:
            query += " AND pid <> pg_backend_pid()"

        cursor.execute(query, (database,))
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()
