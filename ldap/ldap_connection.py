"""
Gestión de conexiones LDAP/Active Directory.

Este módulo proporciona funciones para conectarse a servidores LDAP
usando variables de entorno o parámetros explícitos.

Requiere: pip install ldap3
"""
import os
from typing import Optional
from ldap3 import Server, Connection, ALL, SIMPLE, NTLM, ANONYMOUS


def get_ldap_connection(
    server: Optional[str] = None,
    port: Optional[int] = None,
    use_ssl: bool = False,
    bind_dn: Optional[str] = None,
    bind_password: Optional[str] = None,
    base_dn: Optional[str] = None,
    auth_type: str = 'SIMPLE',
    auto_bind: bool = True
) -> Connection:
    """
    Obtiene conexión a servidor LDAP/Active Directory.

    Los parámetros son opcionales y se toman de variables de entorno si no se especifican.

    Args:
        server: URL del servidor LDAP (ej: 'ldap.empresa.com')
        port: Puerto LDAP (default: 389 para LDAP, 636 para LDAPS)
        use_ssl: Si True, usa LDAPS (SSL/TLS)
        bind_dn: DN para autenticación (ej: 'CN=admin,DC=empresa,DC=com')
        bind_password: Contraseña para autenticación
        base_dn: Base DN para búsquedas (ej: 'DC=empresa,DC=com')
        auth_type: Tipo de autenticación ('SIMPLE', 'NTLM', 'ANONYMOUS')
        auto_bind: Si True, realiza bind automáticamente

    Returns:
        Objeto Connection de ldap3

    Environment Variables:
        LDAP_SERVER: Servidor LDAP (requerido)
        LDAP_PORT: Puerto LDAP (opcional, default: 389 o 636 según SSL)
        LDAP_USE_SSL: 'true' o 'false' para SSL (opcional, default: false)
        LDAP_BASE_DN: Base DN (opcional si LDAP_BIND_DN contiene el dominio)
        LDAP_BIND_DN: DN para bind en formato UPN (usuario@dominio.com) o DN completo
        LDAP_BIND_PASSWORD: Password para bind
        LDAP_AUTH_TYPE: Tipo de autenticación (opcional, default: SIMPLE)

    Nota:
        Si LDAP_BASE_DN no está especificado, se derivará automáticamente de LDAP_BIND_DN:
        - De UPN: usuario@empresa.local -> DC=empresa,DC=local
        - De DN: CN=usuario,DC=empresa,DC=local -> DC=empresa,DC=local

    Example:
        >>> # Usando variables de entorno
        >>> conn = get_ldap_connection()
        >>>
        >>> # Con parámetros explícitos
        >>> conn = get_ldap_connection(
        ...     server='ldap.empresa.com',
        ...     bind_dn='CN=admin,DC=empresa,DC=com',
        ...     bind_password='password123'
        ... )

    Raises:
        ValueError: Si faltan parámetros requeridos
        LDAPException: Si falla la conexión
    """
    # Obtener configuración de variables de entorno o parámetros
    ldap_server = server or os.getenv('LDAP_SERVER')
    ldap_port = port or (int(os.getenv('LDAP_PORT')) if os.getenv('LDAP_PORT') else None)
    ldap_use_ssl = use_ssl or os.getenv('LDAP_USE_SSL', 'false').lower() == 'true'
    ldap_bind_dn = bind_dn or os.getenv('LDAP_BIND_DN')
    ldap_bind_password = bind_password or os.getenv('LDAP_BIND_PASSWORD')
    ldap_base_dn = base_dn or os.getenv('LDAP_BASE_DN')
    ldap_auth_type = auth_type or os.getenv('LDAP_AUTH_TYPE', 'SIMPLE').upper()

    # Validar parámetros requeridos
    if not ldap_server:
        raise ValueError(
            "Servidor LDAP no especificado. "
            "Proporcione el parámetro 'server' o configure LDAP_SERVER en variables de entorno."
        )

    # Si BASE_DN no está especificado, intentar derivarlo del BIND_DN
    if not ldap_base_dn and ldap_bind_dn:
        # Si BIND_DN tiene formato UPN (usuario@dominio.com), extraer el dominio
        if '@' in ldap_bind_dn:
            domain = ldap_bind_dn.split('@')[1]
            # Convertir dominio.com a DC=dominio,DC=com
            ldap_base_dn = ','.join([f'DC={part}' for part in domain.split('.')])
        # Si BIND_DN tiene formato DN (CN=usuario,DC=dominio,DC=com), extraer las partes DC
        elif 'DC=' in ldap_bind_dn.upper():
            # Extraer solo las partes DC del BIND_DN
            parts = ldap_bind_dn.split(',')
            dc_parts = [part.strip() for part in parts if part.strip().upper().startswith('DC=')]
            if dc_parts:
                ldap_base_dn = ','.join(dc_parts)

    if not ldap_base_dn:
        raise ValueError(
            "Base DN no especificado. "
            "Proporcione el parámetro 'base_dn', configure LDAP_BASE_DN en variables de entorno, "
            "o use LDAP_BIND_DN en formato UPN (usuario@dominio.com) o DN completo."
        )

    # Determinar puerto por defecto si no se especifica
    if not ldap_port:
        ldap_port = 636 if ldap_use_ssl else 389

    # Crear servidor
    server_obj = Server(
        ldap_server,
        port=ldap_port,
        use_ssl=ldap_use_ssl,
        get_info=ALL
    )

    # Determinar tipo de autenticación
    auth_method = SIMPLE
    if ldap_auth_type == 'NTLM':
        auth_method = NTLM
    elif ldap_auth_type == 'ANONYMOUS':
        auth_method = ANONYMOUS

    # Crear conexión
    conn = Connection(
        server_obj,
        user=ldap_bind_dn,
        password=ldap_bind_password,
        authentication=auth_method,
        auto_bind=auto_bind
    )

    return conn


def test_ldap_connection(
    server: Optional[str] = None,
    port: Optional[int] = None,
    use_ssl: bool = False,
    bind_dn: Optional[str] = None,
    bind_password: Optional[str] = None,
    base_dn: Optional[str] = None
) -> dict:
    """
    Prueba la conexión LDAP y retorna información del servidor.

    Args:
        server: URL del servidor LDAP
        port: Puerto LDAP
        use_ssl: Si True, usa LDAPS
        bind_dn: DN para autenticación
        bind_password: Contraseña
        base_dn: Base DN

    Returns:
        Dict con información de conexión:
        - success: True/False
        - info: Información del servidor (si success=True)
        - error: Mensaje de error (si success=False)

    Example:
        >>> result = test_ldap_connection()
        >>> if result['success']:
        ...     print(f"Servidor: {result['info']['server']}")
        ...     print(f"Versión: {result['info']['version']}")
        >>> else:
        ...     print(f"Error: {result['error']}")
    """
    try:
        conn = get_ldap_connection(
            server=server,
            port=port,
            use_ssl=use_ssl,
            bind_dn=bind_dn,
            bind_password=bind_password,
            base_dn=base_dn
        )

        # Obtener información del servidor
        server_info = {
            'server': conn.server.host,
            'port': conn.server.port,
            'ssl': conn.server.ssl,
            'version': conn.server.info.supported_ldap_versions if conn.server.info else None,
            'naming_contexts': conn.server.info.naming_contexts if conn.server.info else None,
            'bound': conn.bound,
            'user': conn.user
        }

        conn.unbind()

        return {
            'success': True,
            'info': server_info
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def close_ldap_connection(conn: Connection) -> None:
    """
    Cierra una conexión LDAP de forma segura.

    Args:
        conn: Objeto Connection a cerrar

    Example:
        >>> conn = get_ldap_connection()
        >>> try:
        ...     # Usar conexión
        ...     pass
        >>> finally:
        ...     close_ldap_connection(conn)
    """
    if conn and conn.bound:
        conn.unbind()
