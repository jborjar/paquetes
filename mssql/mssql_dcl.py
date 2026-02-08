"""
Funciones DCL (Data Control Language) para SQL Server.

Este módulo proporciona funciones para control de acceso y permisos:
- Gestión de usuarios (logins)
- Gestión de permisos (GRANT, REVOKE, DENY)
- Gestión de roles
- Gestión de schemas

⚠️ ADVERTENCIA: Las operaciones DCL modifican permisos y seguridad.
Solo deben ser ejecutadas por administradores de base de datos.
"""
import pyodbc
from typing import List, Dict, Any
from .mssql_dml import get_mssql_connection


# ============================================================================
# GESTIÓN DE LOGINS (SERVER LEVEL)
# ============================================================================

def login_exists(login_name: str) -> bool:
    """
    Verifica si un login existe en el servidor SQL Server.

    Args:
        login_name: Nombre del login

    Returns:
        True si el login existe, False en caso contrario

    Example:
        if login_exists('mi_usuario'):
            print('El login existe')
    """
    conn = get_mssql_connection(database='master')
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM sys.server_principals WHERE name = ? AND type IN ('S', 'U')",
            (login_name,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_login(
    login_name: str,
    password: str,
    default_database: str = 'master',
    if_not_exists: bool = True
) -> bool:
    """
    Crea un login (autenticación SQL Server) en el servidor.

    Args:
        login_name: Nombre del login
        password: Contraseña del login
        default_database: Base de datos por defecto (default: 'master')
        if_not_exists: Si True, solo crea si no existe (default: True)

    Returns:
        True si se creó el login, False si ya existía

    Example:
        create_login('app_user', 'P@ssw0rd!123', default_database='API_MCP')
    """
    conn = get_mssql_connection(database='master')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if if_not_exists and login_exists(login_name):
            return False

        cursor.execute(f"""
            CREATE LOGIN [{login_name}]
            WITH PASSWORD = '{password}',
            DEFAULT_DATABASE = [{default_database}],
            CHECK_POLICY = OFF,
            CHECK_EXPIRATION = OFF
        """)
        return True
    finally:
        cursor.close()
        conn.close()


def drop_login(login_name: str, if_exists: bool = True) -> bool:
    """
    Elimina un login del servidor SQL Server.

    Args:
        login_name: Nombre del login
        if_exists: Si True, no genera error si no existe (default: True)

    Returns:
        True si se eliminó el login, False si no existía

    Example:
        drop_login('app_user')
    """
    conn = get_mssql_connection(database='master')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        if if_exists and not login_exists(login_name):
            return False

        cursor.execute(f"DROP LOGIN [{login_name}]")
        return True
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# GESTIÓN DE USUARIOS (DATABASE LEVEL)
# ============================================================================

def user_exists(user_name: str, database: str | None = None) -> bool:
    """
    Verifica si un usuario existe en una base de datos.

    Args:
        user_name: Nombre del usuario
        database: Base de datos opcional

    Returns:
        True si el usuario existe, False en caso contrario

    Example:
        if user_exists('app_user', database='API_MCP'):
            print('El usuario existe')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM sys.database_principals WHERE name = ? AND type IN ('S', 'U')",
            (user_name,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_user(
    user_name: str,
    login_name: str | None = None,
    default_schema: str = 'dbo',
    if_not_exists: bool = True,
    database: str | None = None
) -> bool:
    """
    Crea un usuario en una base de datos.

    Args:
        user_name: Nombre del usuario
        login_name: Nombre del login asociado (si None, usa user_name)
        default_schema: Schema por defecto (default: 'dbo')
        if_not_exists: Si True, solo crea si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se creó el usuario, False si ya existía

    Example:
        create_user('app_user', login_name='app_user', database='API_MCP')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        if if_not_exists and user_exists(user_name, database):
            return False

        login = login_name if login_name else user_name
        cursor.execute(f"""
            CREATE USER [{user_name}]
            FOR LOGIN [{login}]
            WITH DEFAULT_SCHEMA = [{default_schema}]
        """)
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def drop_user(user_name: str, if_exists: bool = True, database: str | None = None) -> bool:
    """
    Elimina un usuario de una base de datos.

    Args:
        user_name: Nombre del usuario
        if_exists: Si True, no genera error si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se eliminó el usuario, False si no existía

    Example:
        drop_user('app_user', database='API_MCP')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        if if_exists and not user_exists(user_name, database):
            return False

        cursor.execute(f"DROP USER [{user_name}]")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# GESTIÓN DE PERMISOS
# ============================================================================

def grant_permission(
    permission: str,
    object_name: str | None = None,
    user_name: str | None = None,
    database: str | None = None
) -> None:
    """
    Otorga un permiso a un usuario.

    Args:
        permission: Tipo de permiso (SELECT, INSERT, UPDATE, DELETE, EXECUTE, etc.)
        object_name: Nombre del objeto (tabla, vista, procedimiento). Si None, otorga a nivel BD
        user_name: Nombre del usuario que recibe el permiso
        database: Base de datos opcional

    Example:
        # Permiso a nivel de tabla
        grant_permission('SELECT', 'SAP_EMPRESAS', 'app_user')

        # Permiso a nivel de base de datos
        grant_permission('CREATE TABLE', user_name='app_user')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        if object_name:
            cursor.execute(f"GRANT {permission} ON {object_name} TO [{user_name}]")
        else:
            cursor.execute(f"GRANT {permission} TO [{user_name}]")

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def revoke_permission(
    permission: str,
    object_name: str | None = None,
    user_name: str | None = None,
    database: str | None = None
) -> None:
    """
    Revoca un permiso de un usuario.

    Args:
        permission: Tipo de permiso (SELECT, INSERT, UPDATE, DELETE, EXECUTE, etc.)
        object_name: Nombre del objeto (tabla, vista, procedimiento). Si None, revoca a nivel BD
        user_name: Nombre del usuario
        database: Base de datos opcional

    Example:
        revoke_permission('DELETE', 'SAP_EMPRESAS', 'app_user')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        if object_name:
            cursor.execute(f"REVOKE {permission} ON {object_name} FROM [{user_name}]")
        else:
            cursor.execute(f"REVOKE {permission} FROM [{user_name}]")

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def deny_permission(
    permission: str,
    object_name: str | None = None,
    user_name: str | None = None,
    database: str | None = None
) -> None:
    """
    Deniega explícitamente un permiso a un usuario.

    NOTA: DENY tiene prioridad sobre GRANT. Usar con precaución.

    Args:
        permission: Tipo de permiso (SELECT, INSERT, UPDATE, DELETE, EXECUTE, etc.)
        object_name: Nombre del objeto (tabla, vista, procedimiento). Si None, deniega a nivel BD
        user_name: Nombre del usuario
        database: Base de datos opcional

    Example:
        deny_permission('DELETE', 'SAP_EMPRESAS', 'readonly_user')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        if object_name:
            cursor.execute(f"DENY {permission} ON {object_name} TO [{user_name}]")
        else:
            cursor.execute(f"DENY {permission} TO [{user_name}]")

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def grant_table_permissions(
    table: str,
    user_name: str,
    permissions: List[str],
    database: str | None = None
) -> None:
    """
    Otorga múltiples permisos sobre una tabla a un usuario.

    Args:
        table: Nombre de la tabla
        user_name: Nombre del usuario
        permissions: Lista de permisos (SELECT, INSERT, UPDATE, DELETE, etc.)
        database: Base de datos opcional

    Example:
        grant_table_permissions(
            'SAP_EMPRESAS',
            'app_user',
            ['SELECT', 'INSERT', 'UPDATE']
        )
    """
    for permission in permissions:
        grant_permission(permission, table, user_name, database)


def get_user_permissions(user_name: str, database: str | None = None) -> List[Dict[str, Any]]:
    """
    Obtiene los permisos de un usuario en la base de datos.

    Args:
        user_name: Nombre del usuario
        database: Base de datos opcional

    Returns:
        Lista de diccionarios con información de permisos

    Example:
        permisos = get_user_permissions('app_user')
        for p in permisos:
            print(f"{p['object']}: {p['permission']} ({p['state']})")
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                pr.type_desc as principal_type,
                pr.name as principal_name,
                pe.state_desc as state,
                pe.permission_name,
                OBJECT_NAME(pe.major_id) as object_name,
                SCHEMA_NAME(o.schema_id) as schema_name
            FROM sys.database_permissions pe
            INNER JOIN sys.database_principals pr ON pe.grantee_principal_id = pr.principal_id
            LEFT JOIN sys.objects o ON pe.major_id = o.object_id
            WHERE pr.name = ?
            ORDER BY pe.permission_name, object_name
        """, (user_name,))

        permissions = []
        for row in cursor.fetchall():
            permissions.append({
                'principal_type': row.principal_type,
                'principal_name': row.principal_name,
                'state': row.state,
                'permission': row.permission_name,
                'object': f"{row.schema_name}.{row.object_name}" if row.object_name else 'DATABASE',
            })

        return permissions
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# GESTIÓN DE ROLES
# ============================================================================

def role_exists(role_name: str, database: str | None = None) -> bool:
    """
    Verifica si un rol existe en una base de datos.

    Args:
        role_name: Nombre del rol
        database: Base de datos opcional

    Returns:
        True si el rol existe, False en caso contrario

    Example:
        if role_exists('app_readonly'):
            print('El rol existe')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM sys.database_principals WHERE name = ? AND type = 'R'",
            (role_name,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_role(role_name: str, if_not_exists: bool = True, database: str | None = None) -> bool:
    """
    Crea un rol en una base de datos.

    Args:
        role_name: Nombre del rol
        if_not_exists: Si True, solo crea si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se creó el rol, False si ya existía

    Example:
        create_role('app_readonly')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        if if_not_exists and role_exists(role_name, database):
            return False

        cursor.execute(f"CREATE ROLE [{role_name}]")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def drop_role(role_name: str, if_exists: bool = True, database: str | None = None) -> bool:
    """
    Elimina un rol de una base de datos.

    Args:
        role_name: Nombre del rol
        if_exists: Si True, no genera error si no existe (default: True)
        database: Base de datos opcional

    Returns:
        True si se eliminó el rol, False si no existía

    Example:
        drop_role('app_readonly')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        if if_exists and not role_exists(role_name, database):
            return False

        cursor.execute(f"DROP ROLE [{role_name}]")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def add_user_to_role(user_name: str, role_name: str, database: str | None = None) -> None:
    """
    Agrega un usuario a un rol.

    Args:
        user_name: Nombre del usuario
        role_name: Nombre del rol
        database: Base de datos opcional

    Example:
        add_user_to_role('app_user', 'db_datareader')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute(f"ALTER ROLE [{role_name}] ADD MEMBER [{user_name}]")
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def remove_user_from_role(user_name: str, role_name: str, database: str | None = None) -> None:
    """
    Remueve un usuario de un rol.

    Args:
        user_name: Nombre del usuario
        role_name: Nombre del rol
        database: Base de datos opcional

    Example:
        remove_user_from_role('app_user', 'db_datareader')
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute(f"ALTER ROLE [{role_name}] DROP MEMBER [{user_name}]")
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_user_roles(user_name: str, database: str | None = None) -> List[str]:
    """
    Obtiene los roles de un usuario.

    Args:
        user_name: Nombre del usuario
        database: Base de datos opcional

    Returns:
        Lista de nombres de roles

    Example:
        roles = get_user_roles('app_user')
        print(f"Roles: {', '.join(roles)}")
    """
    conn = get_mssql_connection(database)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT r.name
            FROM sys.database_role_members rm
            INNER JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
            INNER JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
            WHERE m.name = ?
        """, (user_name,))

        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# UTILIDADES DE SEGURIDAD
# ============================================================================

def create_readonly_user(
    user_name: str,
    login_name: str | None = None,
    password: str | None = None,
    database: str | None = None
) -> Dict[str, bool]:
    """
    Crea un usuario con permisos de solo lectura (SELECT en todas las tablas).

    Args:
        user_name: Nombre del usuario
        login_name: Nombre del login (si None, usa user_name)
        password: Contraseña del login (requerida si el login no existe)
        database: Base de datos opcional

    Returns:
        Diccionario con el resultado de cada operación

    Example:
        result = create_readonly_user('readonly_user', password='Pass123!')
    """
    login = login_name if login_name else user_name
    result = {}

    # Crear login si no existe
    if password and not login_exists(login):
        result['login_created'] = create_login(login, password)
    else:
        result['login_created'] = False

    # Crear usuario
    result['user_created'] = create_user(user_name, login, database=database)

    # Agregar al rol db_datareader
    add_user_to_role(user_name, 'db_datareader', database=database)
    result['role_assigned'] = True

    return result


def create_readwrite_user(
    user_name: str,
    login_name: str | None = None,
    password: str | None = None,
    database: str | None = None
) -> Dict[str, bool]:
    """
    Crea un usuario con permisos de lectura y escritura.

    Args:
        user_name: Nombre del usuario
        login_name: Nombre del login (si None, usa user_name)
        password: Contraseña del login (requerida si el login no existe)
        database: Base de datos opcional

    Returns:
        Diccionario con el resultado de cada operación

    Example:
        result = create_readwrite_user('app_user', password='Pass123!')
    """
    login = login_name if login_name else user_name
    result = {}

    # Crear login si no existe
    if password and not login_exists(login):
        result['login_created'] = create_login(login, password)
    else:
        result['login_created'] = False

    # Crear usuario
    result['user_created'] = create_user(user_name, login, database=database)

    # Agregar a roles
    add_user_to_role(user_name, 'db_datareader', database=database)
    add_user_to_role(user_name, 'db_datawriter', database=database)
    result['roles_assigned'] = True

    return result


# ============================================================================
# GESTIÓN DE CONEXIONES ACTIVAS
# ============================================================================

def get_active_connections(database: str | None = None) -> List[Dict[str, Any]]:
    """
    Obtiene lista de conexiones activas a la base de datos.

    Args:
        database: Base de datos específica (si None, muestra todas las conexiones del servidor)

    Returns:
        Lista de diccionarios con información de cada conexión activa

    Example:
        # Ver todas las conexiones
        conexiones = get_active_connections()
        for conn in conexiones:
            print(f"SPID: {conn['session_id']}, Usuario: {conn['login_name']}, DB: {conn['database_name']}")

        # Ver conexiones de una base de datos específica
        conexiones_api = get_active_connections(database='API_MCP')
    """
    conn = get_mssql_connection(database='master')
    cursor = conn.cursor()

    try:
        if database:
            query = """
                SELECT
                    s.session_id,
                    s.login_time,
                    s.login_name,
                    s.host_name,
                    s.program_name,
                    DB_NAME(s.database_id) as database_name,
                    s.status,
                    s.last_request_start_time,
                    s.last_request_end_time,
                    c.client_net_address,
                    c.connect_time
                FROM sys.dm_exec_sessions s
                LEFT JOIN sys.dm_exec_connections c ON s.session_id = c.session_id
                WHERE s.is_user_process = 1
                AND DB_NAME(s.database_id) = ?
                ORDER BY s.login_time DESC
            """
            cursor.execute(query, (database,))
        else:
            query = """
                SELECT
                    s.session_id,
                    s.login_time,
                    s.login_name,
                    s.host_name,
                    s.program_name,
                    DB_NAME(s.database_id) as database_name,
                    s.status,
                    s.last_request_start_time,
                    s.last_request_end_time,
                    c.client_net_address,
                    c.connect_time
                FROM sys.dm_exec_sessions s
                LEFT JOIN sys.dm_exec_connections c ON s.session_id = c.session_id
                WHERE s.is_user_process = 1
                ORDER BY s.login_time DESC
            """
            cursor.execute(query)

        connections = []
        for row in cursor.fetchall():
            connections.append({
                'session_id': row.session_id,
                'login_time': row.login_time,
                'login_name': row.login_name,
                'host_name': row.host_name,
                'program_name': row.program_name,
                'database_name': row.database_name,
                'status': row.status,
                'last_request_start_time': row.last_request_start_time,
                'last_request_end_time': row.last_request_end_time,
                'client_net_address': row.client_net_address,
                'connect_time': row.connect_time
            })

        return connections
    finally:
        cursor.close()
        conn.close()


def kill_connection(session_id: int) -> bool:
    """
    Cierra (mata) una conexión específica por su session_id.

    ⚠️ ADVERTENCIA: Esta operación termina abruptamente la conexión.
    Usar con precaución.

    Args:
        session_id: ID de la sesión a cerrar (SPID)

    Returns:
        True si se cerró la conexión exitosamente

    Example:
        # Cerrar una conexión específica
        kill_connection(52)
    """
    conn = get_mssql_connection(database='master')
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f"KILL {session_id}")
        return True
    finally:
        cursor.close()
        conn.close()


def kill_all_connections(
    database: str,
    exclude_current: bool = True
) -> int:
    """
    Cierra todas las conexiones activas a una base de datos.

    ⚠️ ADVERTENCIA: Esta operación termina abruptamente todas las conexiones.
    Útil para mantenimiento o antes de eliminar una base de datos.

    Args:
        database: Nombre de la base de datos
        exclude_current: Si True, no cierra la conexión actual (default: True)

    Returns:
        Número de conexiones cerradas

    Example:
        # Cerrar todas las conexiones excepto la actual
        count = kill_all_connections('API_MCP')
        print(f"Se cerraron {count} conexiones")

        # Cerrar absolutamente todas las conexiones
        count = kill_all_connections('API_MCP', exclude_current=False)
    """
    conn = get_mssql_connection(database='master')
    cursor = conn.cursor()

    try:
        # Obtener lista de session_ids activos en la base de datos
        if exclude_current:
            query = """
                SELECT session_id
                FROM sys.dm_exec_sessions
                WHERE database_id = DB_ID(?)
                AND is_user_process = 1
                AND session_id != @@SPID
            """
        else:
            query = """
                SELECT session_id
                FROM sys.dm_exec_sessions
                WHERE database_id = DB_ID(?)
                AND is_user_process = 1
            """

        cursor.execute(query, (database,))
        session_ids = [row.session_id for row in cursor.fetchall()]

        # Cerrar cada conexión
        count = 0
        for session_id in session_ids:
            try:
                cursor.execute(f"KILL {session_id}")
                count += 1
            except Exception:
                # Continuar aunque falle alguna
                pass

        return count
    finally:
        cursor.close()
        conn.close()


def get_connection_count(database: str | None = None) -> int:
    """
    Obtiene el número de conexiones activas.

    Args:
        database: Base de datos específica (si None, cuenta todas las conexiones)

    Returns:
        Número de conexiones activas

    Example:
        # Contar todas las conexiones
        total = get_connection_count()
        print(f"Conexiones totales: {total}")

        # Contar conexiones a una base de datos específica
        count = get_connection_count('API_MCP')
        print(f"Conexiones a API_MCP: {count}")
    """
    conn = get_mssql_connection(database='master')
    cursor = conn.cursor()

    try:
        if database:
            cursor.execute("""
                SELECT COUNT(*)
                FROM sys.dm_exec_sessions
                WHERE database_id = DB_ID(?)
                AND is_user_process = 1
            """, (database,))
        else:
            cursor.execute("""
                SELECT COUNT(*)
                FROM sys.dm_exec_sessions
                WHERE is_user_process = 1
            """)

        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        conn.close()
