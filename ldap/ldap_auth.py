"""
Funciones de autenticación LDAP/Active Directory.

Este módulo proporciona funciones para autenticar usuarios contra LDAP,
verificar credenciales y obtener información de autenticación.
"""
import os
from typing import Optional, Dict
from ldap3 import Server, Connection, ALL, SIMPLE, NTLM
from ldap3.core.exceptions import LDAPException


def authenticate_user(
    username: str,
    password: str,
    server: Optional[str] = None,
    port: Optional[int] = None,
    use_ssl: bool = False,
    base_dn: Optional[str] = None,
    user_dn_template: Optional[str] = None,
    search_filter: Optional[str] = None,
    auth_type: str = 'SIMPLE'
) -> bool:
    """
    Autentica un usuario contra LDAP/Active Directory.

    Puede usar dos métodos:
    1. DN directo con template (ej: 'CN={username},OU=Users,DC=empresa,DC=com')
    2. Búsqueda del usuario por atributo (ej: sAMAccountName, uid)

    Args:
        username: Nombre de usuario
        password: Contraseña
        server: Servidor LDAP (opcional, usa LDAP_SERVER)
        port: Puerto LDAP (opcional)
        use_ssl: Si True, usa LDAPS
        base_dn: Base DN (opcional, usa LDAP_BASE_DN)
        user_dn_template: Template para DN del usuario (ej: 'CN={username},OU=Users,DC=empresa,DC=com')
        search_filter: Filtro para buscar usuario (ej: '(sAMAccountName={username})')
        auth_type: Tipo de autenticación ('SIMPLE' o 'NTLM')

    Returns:
        True si autenticación exitosa, False en caso contrario

    Environment Variables:
        LDAP_SERVER: Servidor LDAP
        LDAP_PORT: Puerto LDAP
        LDAP_USE_SSL: 'true' o 'false'
        LDAP_BASE_DN: Base DN
        LDAP_USER_DN_TEMPLATE: Template para DN de usuario
        LDAP_SEARCH_FILTER: Filtro de búsqueda (default: '(sAMAccountName={username})')
        LDAP_AUTH_TYPE: Tipo de autenticación

    Example:
        >>> # Usando DN template
        >>> authenticate_user('jperez', 'password123')
        True
        >>>
        >>> # Usando búsqueda
        >>> authenticate_user(
        ...     'jperez',
        ...     'password123',
        ...     search_filter='(uid={username})'
        ... )
        True
    """
    try:
        # Obtener configuración
        ldap_server = server or os.getenv('LDAP_SERVER')
        ldap_port = port or (int(os.getenv('LDAP_PORT')) if os.getenv('LDAP_PORT') else None)
        ldap_use_ssl = use_ssl or os.getenv('LDAP_USE_SSL', 'false').lower() == 'true'
        ldap_base_dn = base_dn or os.getenv('LDAP_BASE_DN')
        ldap_user_dn_template = user_dn_template or os.getenv('LDAP_USER_DN_TEMPLATE')
        ldap_search_filter = search_filter or os.getenv('LDAP_SEARCH_FILTER', '(sAMAccountName={username})')
        ldap_auth_type = auth_type or os.getenv('LDAP_AUTH_TYPE', 'SIMPLE').upper()

        if not ldap_server:
            raise ValueError("Servidor LDAP es requerido")

        # Si BASE_DN no está especificado, derivarlo del BIND_DN
        if not ldap_base_dn:
            ldap_bind_dn = os.getenv('LDAP_BIND_DN')
            if ldap_bind_dn and '@' in ldap_bind_dn:
                domain = ldap_bind_dn.split('@')[1]
                ldap_base_dn = ','.join([f'DC={part}' for part in domain.split('.')])
            elif ldap_bind_dn and 'DC=' in ldap_bind_dn.upper():
                parts = ldap_bind_dn.split(',')
                dc_parts = [part.strip() for part in parts if part.strip().upper().startswith('DC=')]
                if dc_parts:
                    ldap_base_dn = ','.join(dc_parts)

        if not ldap_base_dn:
            raise ValueError("Base DN no especificado y no se pudo derivar de LDAP_BIND_DN")

        if not ldap_port:
            ldap_port = 636 if ldap_use_ssl else 389

        # Crear servidor
        server_obj = Server(ldap_server, port=ldap_port, use_ssl=ldap_use_ssl, get_info=ALL)

        # Determinar DN del usuario
        user_dn = None

        if ldap_user_dn_template:
            # Método 1: Usar template de DN
            user_dn = ldap_user_dn_template.format(username=username)

        else:
            # Método 2: Buscar usuario primero con credenciales de administrador
            admin_dn = os.getenv('LDAP_BIND_DN')
            admin_password = os.getenv('LDAP_BIND_PASSWORD')

            if not admin_dn or not admin_password:
                raise ValueError(
                    "Para búsqueda de usuarios se requiere LDAP_BIND_DN y LDAP_BIND_PASSWORD, "
                    "o use LDAP_USER_DN_TEMPLATE"
                )

            # Conectar con admin
            search_conn = Connection(server_obj, user=admin_dn, password=admin_password)
            if not search_conn.bind():
                raise LDAPException("Fallo autenticación de administrador")

            # Buscar usuario
            search_filter_formatted = ldap_search_filter.format(username=username)
            search_conn.search(
                search_base=ldap_base_dn,
                search_filter=search_filter_formatted,
                attributes=['cn']
            )

            if not search_conn.entries:
                search_conn.unbind()
                return False

            user_dn = search_conn.entries[0].entry_dn
            search_conn.unbind()

        # Autenticar con DN del usuario
        auth_method = NTLM if ldap_auth_type == 'NTLM' else SIMPLE

        user_conn = Connection(
            server_obj,
            user=user_dn,
            password=password,
            authentication=auth_method
        )

        # Intentar bind
        if user_conn.bind():
            user_conn.unbind()
            return True
        else:
            return False

    except Exception:
        return False


def get_user_info(
    username: str,
    password: str,
    server: Optional[str] = None,
    port: Optional[int] = None,
    use_ssl: bool = False,
    base_dn: Optional[str] = None,
    search_filter: Optional[str] = None,
    attributes: Optional[list] = None
) -> Optional[Dict]:
    """
    Autentica usuario y retorna su información del directorio.

    Args:
        username: Nombre de usuario
        password: Contraseña
        server: Servidor LDAP
        port: Puerto LDAP
        use_ssl: Si True, usa LDAPS
        base_dn: Base DN
        search_filter: Filtro de búsqueda
        attributes: Lista de atributos a retornar (default: todos)

    Returns:
        Dict con información del usuario si autenticación exitosa, None en caso contrario

    Example:
        >>> user_info = get_user_info('jperez', 'password123')
        >>> if user_info:
        ...     print(f"Nombre: {user_info.get('cn')}")
        ...     print(f"Email: {user_info.get('mail')}")
        ...     print(f"Grupos: {user_info.get('memberOf')}")
    """
    try:
        # Obtener configuración
        ldap_server = server or os.getenv('LDAP_SERVER')
        ldap_port = port or (int(os.getenv('LDAP_PORT')) if os.getenv('LDAP_PORT') else None)
        ldap_use_ssl = use_ssl or os.getenv('LDAP_USE_SSL', 'false').lower() == 'true'
        ldap_base_dn = base_dn or os.getenv('LDAP_BASE_DN')
        ldap_search_filter = search_filter or os.getenv('LDAP_SEARCH_FILTER', '(sAMAccountName={username})')

        if not ldap_server:
            raise ValueError("Servidor LDAP es requerido")

        # Si BASE_DN no está especificado, derivarlo del BIND_DN
        if not ldap_base_dn:
            ldap_bind_dn = os.getenv('LDAP_BIND_DN')
            if ldap_bind_dn and '@' in ldap_bind_dn:
                domain = ldap_bind_dn.split('@')[1]
                ldap_base_dn = ','.join([f'DC={part}' for part in domain.split('.')])
            elif ldap_bind_dn and 'DC=' in ldap_bind_dn.upper():
                parts = ldap_bind_dn.split(',')
                dc_parts = [part.strip() for part in parts if part.strip().upper().startswith('DC=')]
                if dc_parts:
                    ldap_base_dn = ','.join(dc_parts)

        if not ldap_base_dn:
            raise ValueError("Base DN no especificado y no se pudo derivar de LDAP_BIND_DN")

        if not ldap_port:
            ldap_port = 636 if ldap_use_ssl else 389

        # Primero autenticar
        if not authenticate_user(username, password, server, port, use_ssl, base_dn):
            return None

        # Conectar con credenciales de admin para buscar info
        admin_dn = os.getenv('LDAP_BIND_DN')
        admin_password = os.getenv('LDAP_BIND_PASSWORD')

        if not admin_dn or not admin_password:
            raise ValueError("Se requiere LDAP_BIND_DN y LDAP_BIND_PASSWORD")

        server_obj = Server(ldap_server, port=ldap_port, use_ssl=ldap_use_ssl, get_info=ALL)
        conn = Connection(server_obj, user=admin_dn, password=admin_password)

        if not conn.bind():
            return None

        # Buscar usuario
        search_filter_formatted = ldap_search_filter.format(username=username)
        search_attrs = attributes or ['*']

        conn.search(
            search_base=ldap_base_dn,
            search_filter=search_filter_formatted,
            attributes=search_attrs
        )

        if not conn.entries:
            conn.unbind()
            return None

        # Convertir a diccionario
        entry = conn.entries[0]
        user_info = {}

        for attr in entry.entry_attributes:
            value = entry[attr].value
            # Convertir listas de un elemento a valor único
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            user_info[attr] = value

        conn.unbind()
        return user_info

    except Exception:
        return None


def verify_credentials(
    username: str,
    password: str,
    server: Optional[str] = None,
    base_dn: Optional[str] = None
) -> Dict:
    """
    Verifica credenciales y retorna resultado detallado.

    Args:
        username: Nombre de usuario
        password: Contraseña
        server: Servidor LDAP
        base_dn: Base DN

    Returns:
        Dict con:
        - valid: True/False
        - username: Nombre de usuario
        - dn: DN del usuario (si valid=True)
        - error: Mensaje de error (si valid=False)

    Example:
        >>> result = verify_credentials('jperez', 'password123')
        >>> if result['valid']:
        ...     print(f"Usuario válido: {result['dn']}")
        >>> else:
        ...     print(f"Error: {result['error']}")
    """
    try:
        # Obtener configuración
        ldap_server = server or os.getenv('LDAP_SERVER')
        ldap_base_dn = base_dn or os.getenv('LDAP_BASE_DN')
        ldap_search_filter = os.getenv('LDAP_SEARCH_FILTER', '(sAMAccountName={username})')

        if not ldap_server:
            return {
                'valid': False,
                'username': username,
                'error': 'Servidor LDAP no configurado'
            }

        # Si BASE_DN no está especificado, derivarlo del BIND_DN
        if not ldap_base_dn:
            ldap_bind_dn = os.getenv('LDAP_BIND_DN')
            if ldap_bind_dn and '@' in ldap_bind_dn:
                domain = ldap_bind_dn.split('@')[1]
                ldap_base_dn = ','.join([f'DC={part}' for part in domain.split('.')])
            elif ldap_bind_dn and 'DC=' in ldap_bind_dn.upper():
                parts = ldap_bind_dn.split(',')
                dc_parts = [part.strip() for part in parts if part.strip().upper().startswith('DC=')]
                if dc_parts:
                    ldap_base_dn = ','.join(dc_parts)

        if not ldap_base_dn:
            return {
                'valid': False,
                'username': username,
                'error': 'Base DN no especificado y no se pudo derivar de LDAP_BIND_DN'
            }

        # Primero buscar el usuario para obtener su DN
        admin_dn = os.getenv('LDAP_BIND_DN')
        admin_password = os.getenv('LDAP_BIND_PASSWORD')

        if not admin_dn or not admin_password:
            return {
                'valid': False,
                'username': username,
                'error': 'Credenciales de administrador no configuradas'
            }

        server_obj = Server(ldap_server, get_info=ALL)
        search_conn = Connection(server_obj, user=admin_dn, password=admin_password)

        if not search_conn.bind():
            return {
                'valid': False,
                'username': username,
                'error': 'Fallo autenticación de administrador'
            }

        # Buscar usuario
        search_filter_formatted = ldap_search_filter.format(username=username)
        search_conn.search(
            search_base=ldap_base_dn,
            search_filter=search_filter_formatted,
            attributes=['cn']
        )

        if not search_conn.entries:
            search_conn.unbind()
            return {
                'valid': False,
                'username': username,
                'error': 'Usuario no encontrado'
            }

        user_dn = search_conn.entries[0].entry_dn
        search_conn.unbind()

        # Intentar autenticar con credenciales del usuario
        user_conn = Connection(server_obj, user=user_dn, password=password)

        if user_conn.bind():
            user_conn.unbind()
            return {
                'valid': True,
                'username': username,
                'dn': user_dn
            }
        else:
            return {
                'valid': False,
                'username': username,
                'error': 'Contraseña incorrecta'
            }

    except Exception as e:
        return {
            'valid': False,
            'username': username,
            'error': str(e)
        }
