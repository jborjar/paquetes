"""
Ejemplos de validadores de usuarios.

El usuario debe crear su propio validador según su sistema de autenticación
(LDAP, Active Directory, base de datos, etc.) y configurarlo en el .env:

    AUTH_VALIDATOR_MODULE=paquetes.auth.validators
    AUTH_VALIDATOR_FUNCTION=validate_user

Todos los validadores deben tener la firma:
    def validate_user(username: str, password: str) -> bool
"""
import os
import hashlib
from typing import Optional


# ============================================================================
# EJEMPLO 1: Validación contra base de datos MSSQL
# ============================================================================

def validate_user_mssql(username: str, password: str) -> bool:
    """
    Valida usuario contra tabla USERS en MSSQL.

    Estructura de tabla esperada:
    CREATE TABLE USERS (
        Username NVARCHAR(100) PRIMARY KEY,
        PasswordHash NVARCHAR(64) NOT NULL,  -- SHA256
        Active BIT NOT NULL DEFAULT 1
    )

    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano

    Returns:
        True si credenciales son válidas, False en caso contrario
    """
    from paquetes.mssql import select_one

    try:
        # Hash de la contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Buscar usuario
        user = select_one(
            'USERS',
            where={'Username': username, 'PasswordHash': password_hash, 'Active': 1}
        )

        return user is not None

    except Exception:
        return False


# ============================================================================
# EJEMPLO 2: Validación contra LDAP/Active Directory
# ============================================================================

def validate_user_ldap(username: str, password: str) -> bool:
    """
    Valida usuario contra LDAP/Active Directory usando el paquete ldap.

    Variables de entorno requeridas:
    - LDAP_SERVER: Servidor LDAP (ej: 'ldap.empresa.com')
    - LDAP_BASE_DN: Base DN (ej: 'DC=empresa,DC=com')
    - LDAP_BIND_DN: DN de administrador (para búsqueda)
    - LDAP_BIND_PASSWORD: Password de administrador
    - LDAP_SEARCH_FILTER: Filtro de búsqueda (ej: '(sAMAccountName={username})')

    O alternativamente:
    - LDAP_USER_DN_TEMPLATE: Template directo (ej: 'CN={username},OU=Users,DC=empresa,DC=com')

    Args:
        username: Nombre de usuario
        password: Contraseña

    Returns:
        True si credenciales son válidas, False en caso contrario
    """
    try:
        from paquetes.ldap import authenticate_user

        return authenticate_user(username, password)

    except Exception:
        return False


# ============================================================================
# EJEMPLO 3: Validación con usuarios hardcodeados (SOLO DESARROLLO)
# ============================================================================

def validate_user_hardcoded(username: str, password: str) -> bool:
    """
    Valida usuario contra lista hardcodeada.

    ⚠️ SOLO PARA DESARROLLO/TESTING - NO USAR EN PRODUCCIÓN

    Usuarios de prueba:
    - admin / admin123
    - user / user123

    Args:
        username: Nombre de usuario
        password: Contraseña

    Returns:
        True si credenciales son válidas, False en caso contrario
    """
    users = {
        'admin': 'admin123',
        'user': 'user123'
    }

    return users.get(username) == password


# ============================================================================
# EJEMPLO 4: Validación contra SAP HANA
# ============================================================================

def validate_user_hana(username: str, password: str) -> bool:
    """
    Valida usuario contra tabla USERS en SAP HANA.

    Estructura de tabla esperada:
    CREATE TABLE USERS (
        USERNAME NVARCHAR(100) PRIMARY KEY,
        PASSWORD_HASH NVARCHAR(64) NOT NULL,  -- SHA256
        ACTIVE TINYINT NOT NULL DEFAULT 1
    )

    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano

    Returns:
        True si credenciales son válidas, False en caso contrario
    """
    from paquetes.hana import select

    try:
        # Hash de la contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Buscar usuario
        users = select(
            'USERS',
            where=f"USERNAME = '{username}' AND PASSWORD_HASH = '{password_hash}' AND ACTIVE = 1"
        )

        return len(users) > 0

    except Exception:
        return False


# ============================================================================
# EJEMPLO 5: Validación con bcrypt (recomendado para producción)
# ============================================================================

def validate_user_bcrypt(username: str, password: str) -> bool:
    """
    Valida usuario con bcrypt (más seguro que SHA256).

    Requiere: pip install bcrypt

    Estructura de tabla:
    CREATE TABLE USERS (
        Username NVARCHAR(100) PRIMARY KEY,
        PasswordHash NVARCHAR(60) NOT NULL,  -- bcrypt hash
        Active BIT NOT NULL DEFAULT 1
    )

    Para crear hash:
        import bcrypt
        password_hash = bcrypt.hashpw('password'.encode(), bcrypt.gensalt()).decode()

    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano

    Returns:
        True si credenciales son válidas, False en caso contrario
    """
    try:
        import bcrypt
        from paquetes.mssql import select_one

        # Buscar usuario
        user = select_one('USERS', where={'Username': username, 'Active': 1})

        if not user:
            return False

        # Verificar contraseña con bcrypt
        stored_hash = user['PasswordHash'].encode()
        return bcrypt.checkpw(password.encode(), stored_hash)

    except Exception:
        return False
