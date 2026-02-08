"""
Funciones DCL (Data Control Language) para SAP HANA.

Este módulo proporciona funciones para control de acceso y permisos:
- Gestión de usuarios
- Gestión de permisos (GRANT, REVOKE)
- Gestión de roles
- Gestión de conexiones

⚠️ ADVERTENCIA: Las operaciones DCL modifican permisos y seguridad.
Solo deben ser ejecutadas por administradores de base de datos.
"""
from hdbcli import dbapi
from typing import List, Dict, Any
from .hana_dml import get_hana_connection


# ============================================================================
# GESTIÓN DE USUARIOS
# ============================================================================

def user_exists(user_name: str) -> bool:
    """
    Verifica si un usuario existe en SAP HANA.

    Args:
        user_name: Nombre del usuario

    Returns:
        True si el usuario existe, False en caso contrario

    Example:
        if user_exists('APP_USER'):
            print('El usuario existe')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM SYS.USERS WHERE USER_NAME = ?",
            (user_name,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_user(
    user_name: str,
    password: str,
    if_not_exists: bool = True
) -> bool:
    """
    Crea un usuario en SAP HANA.

    Args:
        user_name: Nombre del usuario
        password: Contraseña del usuario
        if_not_exists: Si True, solo crea si no existe (default: True)

    Returns:
        True si se creó el usuario, False si ya existía

    Example:
        create_user('APP_USER', 'SecureP@ss123')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        if if_not_exists and user_exists(user_name):
            return False

        cursor.execute(f"CREATE USER {user_name} PASSWORD {password}")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def drop_user(user_name: str, if_exists: bool = True) -> bool:
    """
    Elimina un usuario de SAP HANA.

    Args:
        user_name: Nombre del usuario
        if_exists: Si True, no genera error si no existe (default: True)

    Returns:
        True si se eliminó el usuario, False si no existía

    Example:
        drop_user('APP_USER')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        if if_exists and not user_exists(user_name):
            return False

        cursor.execute(f"DROP USER {user_name} CASCADE")
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
    schema: str | None = None
) -> None:
    """
    Otorga un permiso a un usuario.

    Args:
        permission: Tipo de permiso (SELECT, INSERT, UPDATE, DELETE, EXECUTE, etc.)
        object_name: Nombre del objeto (tabla, vista, procedimiento). Si None, otorga a nivel schema
        user_name: Nombre del usuario que recibe el permiso
        schema: Schema opcional

    Example:
        # Permiso a nivel de tabla
        grant_permission('SELECT', 'OITM', 'APP_USER', schema='SBODEMOUY')

        # Permiso a nivel de schema
        grant_permission('SELECT', user_name='APP_USER', schema='SBODEMOUY')
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        if object_name:
            cursor.execute(f"GRANT {permission} ON {object_name} TO {user_name}")
        elif schema:
            cursor.execute(f"GRANT {permission} ON SCHEMA {schema} TO {user_name}")
        else:
            cursor.execute(f"GRANT {permission} TO {user_name}")

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def revoke_permission(
    permission: str,
    object_name: str | None = None,
    user_name: str | None = None,
    schema: str | None = None
) -> None:
    """
    Revoca un permiso de un usuario.

    Args:
        permission: Tipo de permiso (SELECT, INSERT, UPDATE, DELETE, EXECUTE, etc.)
        object_name: Nombre del objeto (tabla, vista, procedimiento). Si None, revoca a nivel schema
        user_name: Nombre del usuario
        schema: Schema opcional

    Example:
        revoke_permission('DELETE', 'OITM', 'APP_USER', schema='SBODEMOUY')
    """
    conn = get_hana_connection(schema)
    cursor = conn.cursor()

    try:
        if object_name:
            cursor.execute(f"REVOKE {permission} ON {object_name} FROM {user_name}")
        elif schema:
            cursor.execute(f"REVOKE {permission} ON SCHEMA {schema} FROM {user_name}")
        else:
            cursor.execute(f"REVOKE {permission} FROM {user_name}")

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_user_permissions(user_name: str) -> List[Dict[str, Any]]:
    """
    Obtiene los permisos de un usuario en la base de datos.

    Args:
        user_name: Nombre del usuario

    Returns:
        Lista de diccionarios con información de permisos

    Example:
        permisos = get_user_permissions('APP_USER')
        for p in permisos:
            print(f"{p['object']}: {p['privilege']}")
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                GRANTEE,
                GRANTOR,
                SCHEMA_NAME,
                OBJECT_NAME,
                OBJECT_TYPE,
                PRIVILEGE,
                IS_GRANTABLE
            FROM SYS.GRANTED_PRIVILEGES
            WHERE GRANTEE = ?
            ORDER BY SCHEMA_NAME, OBJECT_NAME, PRIVILEGE
        """, (user_name,))

        permissions = []
        for row in cursor.fetchall():
            object_desc = f"{row[2]}.{row[3]}" if row[3] else row[2]
            permissions.append({
                'grantee': row[0],
                'grantor': row[1],
                'schema': row[2],
                'object_name': row[3],
                'object_type': row[4],
                'privilege': row[5],
                'is_grantable': row[6] == 'TRUE',
                'object': object_desc
            })

        return permissions
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# GESTIÓN DE ROLES
# ============================================================================

def role_exists(role_name: str) -> bool:
    """
    Verifica si un rol existe en SAP HANA.

    Args:
        role_name: Nombre del rol

    Returns:
        True si el rol existe, False en caso contrario

    Example:
        if role_exists('APP_READONLY'):
            print('El rol existe')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM SYS.ROLES WHERE ROLE_NAME = ?",
            (role_name,)
        )
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()


def create_role(role_name: str, if_not_exists: bool = True) -> bool:
    """
    Crea un rol en SAP HANA.

    Args:
        role_name: Nombre del rol
        if_not_exists: Si True, solo crea si no existe (default: True)

    Returns:
        True si se creó el rol, False si ya existía

    Example:
        create_role('APP_READONLY')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        if if_not_exists and role_exists(role_name):
            return False

        cursor.execute(f"CREATE ROLE {role_name}")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def drop_role(role_name: str, if_exists: bool = True) -> bool:
    """
    Elimina un rol de SAP HANA.

    Args:
        role_name: Nombre del rol
        if_exists: Si True, no genera error si no existe (default: True)

    Returns:
        True si se eliminó el rol, False si no existía

    Example:
        drop_role('APP_READONLY')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        if if_exists and not role_exists(role_name):
            return False

        cursor.execute(f"DROP ROLE {role_name}")
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()


def grant_role(role_name: str, user_name: str) -> None:
    """
    Asigna un rol a un usuario.

    Args:
        role_name: Nombre del rol
        user_name: Nombre del usuario

    Example:
        grant_role('APP_READONLY', 'APP_USER')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"GRANT {role_name} TO {user_name}")
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def revoke_role(role_name: str, user_name: str) -> None:
    """
    Revoca un rol de un usuario.

    Args:
        role_name: Nombre del rol
        user_name: Nombre del usuario

    Example:
        revoke_role('APP_READONLY', 'APP_USER')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"REVOKE {role_name} FROM {user_name}")
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_user_roles(user_name: str) -> List[str]:
    """
    Obtiene los roles de un usuario.

    Args:
        user_name: Nombre del usuario

    Returns:
        Lista de nombres de roles

    Example:
        roles = get_user_roles('APP_USER')
        print(f"Roles: {', '.join(roles)}")
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT ROLE_NAME
            FROM SYS.GRANTED_ROLES
            WHERE GRANTEE = ?
            ORDER BY ROLE_NAME
        """, (user_name,))

        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# GESTIÓN DE CONEXIONES ACTIVAS
# ============================================================================

def get_active_connections(user_name: str | None = None) -> List[Dict[str, Any]]:
    """
    Obtiene lista de conexiones activas en SAP HANA.

    Args:
        user_name: Usuario específico (si None, muestra todas las conexiones)

    Returns:
        Lista de diccionarios con información de cada conexión activa

    Example:
        # Ver todas las conexiones
        conexiones = get_active_connections()
        for conn in conexiones:
            print(f"Connection ID: {conn['connection_id']}, User: {conn['user_name']}")

        # Ver conexiones de un usuario específico
        conexiones_user = get_active_connections(user_name='APP_USER')
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        if user_name:
            query = """
                SELECT
                    CONNECTION_ID,
                    CONNECTION_STATUS,
                    USER_NAME,
                    CLIENT_HOST,
                    CLIENT_IP,
                    CLIENT_PID,
                    START_TIME,
                    IDLE_TIME,
                    CURRENT_SCHEMA_NAME,
                    CURRENT_STATEMENT_ID,
                    CONNECTION_TYPE
                FROM SYS.M_CONNECTIONS
                WHERE USER_NAME = ?
                ORDER BY START_TIME DESC
            """
            cursor.execute(query, (user_name,))
        else:
            query = """
                SELECT
                    CONNECTION_ID,
                    CONNECTION_STATUS,
                    USER_NAME,
                    CLIENT_HOST,
                    CLIENT_IP,
                    CLIENT_PID,
                    START_TIME,
                    IDLE_TIME,
                    CURRENT_SCHEMA_NAME,
                    CURRENT_STATEMENT_ID,
                    CONNECTION_TYPE
                FROM SYS.M_CONNECTIONS
                ORDER BY START_TIME DESC
            """
            cursor.execute(query)

        connections = []
        for row in cursor.fetchall():
            connections.append({
                'connection_id': row[0],
                'connection_status': row[1],
                'user_name': row[2],
                'client_host': row[3],
                'client_ip': row[4],
                'client_pid': row[5],
                'start_time': row[6],
                'idle_time': row[7],
                'current_schema': row[8],
                'current_statement_id': row[9],
                'connection_type': row[10]
            })

        return connections
    finally:
        cursor.close()
        conn.close()


def get_connection_count(user_name: str | None = None) -> int:
    """
    Obtiene el número de conexiones activas.

    Args:
        user_name: Usuario específico (si None, cuenta todas las conexiones)

    Returns:
        Número de conexiones activas

    Example:
        # Contar todas las conexiones
        total = get_connection_count()
        print(f"Conexiones totales: {total}")

        # Contar conexiones de un usuario específico
        count = get_connection_count('APP_USER')
        print(f"Conexiones de APP_USER: {count}")
    """
    conn = get_hana_connection()
    cursor = conn.cursor()

    try:
        if user_name:
            cursor.execute("""
                SELECT COUNT(*)
                FROM SYS.M_CONNECTIONS
                WHERE USER_NAME = ?
            """, (user_name,))
        else:
            cursor.execute("SELECT COUNT(*) FROM SYS.M_CONNECTIONS")

        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# UTILIDADES DE SEGURIDAD
# ============================================================================

def create_readonly_user(
    user_name: str,
    password: str,
    schema: str
) -> Dict[str, bool]:
    """
    Crea un usuario con permisos de solo lectura en un schema.

    Args:
        user_name: Nombre del usuario
        password: Contraseña del usuario
        schema: Schema al que tendrá acceso

    Returns:
        Diccionario con el resultado de cada operación

    Example:
        result = create_readonly_user('READONLY_USER', 'Pass123!', 'SBODEMOUY')
    """
    result = {}

    # Crear usuario
    result['user_created'] = create_user(user_name, password)

    # Otorgar permiso SELECT en el schema
    try:
        grant_permission('SELECT', user_name=user_name, schema=schema)
        result['permission_granted'] = True
    except Exception:
        result['permission_granted'] = False

    return result


def create_readwrite_user(
    user_name: str,
    password: str,
    schema: str
) -> Dict[str, bool]:
    """
    Crea un usuario con permisos de lectura y escritura en un schema.

    Args:
        user_name: Nombre del usuario
        password: Contraseña del usuario
        schema: Schema al que tendrá acceso

    Returns:
        Diccionario con el resultado de cada operación

    Example:
        result = create_readwrite_user('APP_USER', 'Pass123!', 'SBODEMOUY')
    """
    result = {}

    # Crear usuario
    result['user_created'] = create_user(user_name, password)

    # Otorgar permisos en el schema
    try:
        grant_permission('SELECT', user_name=user_name, schema=schema)
        grant_permission('INSERT', user_name=user_name, schema=schema)
        grant_permission('UPDATE', user_name=user_name, schema=schema)
        grant_permission('DELETE', user_name=user_name, schema=schema)
        result['permissions_granted'] = True
    except Exception:
        result['permissions_granted'] = False

    return result
