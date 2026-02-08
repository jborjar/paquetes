"""
Funciones de búsqueda en LDAP/Active Directory.

Este módulo proporciona funciones para buscar usuarios, grupos,
unidades organizativas y otros objetos en el directorio LDAP.
"""
from typing import List, Dict, Optional, Any
from ldap3.core.exceptions import LDAPException
from .ldap_connection import get_ldap_connection, close_ldap_connection


def search_users(
    filter_query: Optional[str] = None,
    attributes: Optional[List[str]] = None,
    base_dn: Optional[str] = None,
    limit: int = 0
) -> List[Dict[str, Any]]:
    """
    Busca usuarios en el directorio LDAP.

    Args:
        filter_query: Filtro LDAP (default: '(objectClass=person)')
        attributes: Lista de atributos a retornar (default: ['cn', 'sAMAccountName', 'mail', 'memberOf'])
        base_dn: Base DN para búsqueda (opcional, usa LDAP_BASE_DN)
        limit: Límite de resultados (0 = sin límite)

    Returns:
        Lista de diccionarios con información de usuarios

    Example:
        >>> # Buscar todos los usuarios
        >>> users = search_users()
        >>>
        >>> # Buscar usuarios activos
        >>> users = search_users(filter_query='(&(objectClass=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))')
        >>>
        >>> # Buscar por nombre
        >>> users = search_users(filter_query='(cn=*Juan*)')
        >>>
        >>> for user in users:
        ...     print(f"{user['cn']} - {user['mail']}")
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Configurar búsqueda
        search_filter = filter_query or '(objectClass=person)'
        search_attrs = attributes or ['cn', 'sAMAccountName', 'mail', 'memberOf']
        search_base = base_dn or conn.server.info.naming_contexts[0]

        # Ejecutar búsqueda
        conn.search(
            search_base=search_base,
            search_filter=search_filter,
            attributes=search_attrs,
            size_limit=limit
        )

        # Convertir resultados a lista de diccionarios
        results = []
        for entry in conn.entries:
            user_dict = {'dn': entry.entry_dn}
            for attr in entry.entry_attributes:
                value = entry[attr].value
                # Convertir listas de un elemento a valor único
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                user_dict[attr] = value
            results.append(user_dict)

        return results

    except LDAPException as e:
        raise Exception(f"Error buscando usuarios: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def search_groups(
    filter_query: Optional[str] = None,
    attributes: Optional[List[str]] = None,
    base_dn: Optional[str] = None,
    limit: int = 0
) -> List[Dict[str, Any]]:
    """
    Busca grupos en el directorio LDAP.

    Args:
        filter_query: Filtro LDAP (default: '(objectClass=group)')
        attributes: Lista de atributos a retornar
        base_dn: Base DN para búsqueda
        limit: Límite de resultados (0 = sin límite)

    Returns:
        Lista de diccionarios con información de grupos

    Example:
        >>> # Buscar todos los grupos
        >>> groups = search_groups()
        >>>
        >>> # Buscar grupos de seguridad
        >>> groups = search_groups(filter_query='(&(objectClass=group)(groupType:1.2.840.113556.1.4.803:=2147483648))')
        >>>
        >>> # Buscar por nombre
        >>> groups = search_groups(filter_query='(cn=Administradores*)')
        >>>
        >>> for group in groups:
        ...     print(f"{group['cn']} - {len(group.get('member', []))} miembros")
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Configurar búsqueda
        search_filter = filter_query or '(objectClass=group)'
        search_attrs = attributes or ['cn', 'sAMAccountName', 'description', 'member']
        search_base = base_dn or conn.server.info.naming_contexts[0]

        # Ejecutar búsqueda
        conn.search(
            search_base=search_base,
            search_filter=search_filter,
            attributes=search_attrs,
            size_limit=limit
        )

        # Convertir resultados
        results = []
        for entry in conn.entries:
            group_dict = {'dn': entry.entry_dn}
            for attr in entry.entry_attributes:
                value = entry[attr].value
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                group_dict[attr] = value
            results.append(group_dict)

        return results

    except LDAPException as e:
        raise Exception(f"Error buscando grupos: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def search_organizational_units(
    filter_query: Optional[str] = None,
    attributes: Optional[List[str]] = None,
    base_dn: Optional[str] = None,
    limit: int = 0
) -> List[Dict[str, Any]]:
    """
    Busca unidades organizativas (OUs) en el directorio LDAP.

    Args:
        filter_query: Filtro LDAP (default: '(objectClass=organizationalUnit)')
        attributes: Lista de atributos a retornar
        base_dn: Base DN para búsqueda
        limit: Límite de resultados

    Returns:
        Lista de diccionarios con información de OUs

    Example:
        >>> # Buscar todas las OUs
        >>> ous = search_organizational_units()
        >>>
        >>> # Buscar por nombre
        >>> ous = search_organizational_units(filter_query='(ou=Ventas*)')
        >>>
        >>> for ou in ous:
        ...     print(f"{ou['ou']} - {ou['dn']}")
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Configurar búsqueda
        search_filter = filter_query or '(objectClass=organizationalUnit)'
        search_attrs = attributes or ['ou', 'description']
        search_base = base_dn or conn.server.info.naming_contexts[0]

        # Ejecutar búsqueda
        conn.search(
            search_base=search_base,
            search_filter=search_filter,
            attributes=search_attrs,
            size_limit=limit
        )

        # Convertir resultados
        results = []
        for entry in conn.entries:
            ou_dict = {'dn': entry.entry_dn}
            for attr in entry.entry_attributes:
                value = entry[attr].value
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                ou_dict[attr] = value
            results.append(ou_dict)

        return results

    except LDAPException as e:
        raise Exception(f"Error buscando OUs: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def search_custom(
    filter_query: str,
    attributes: Optional[List[str]] = None,
    base_dn: Optional[str] = None,
    scope: str = 'SUBTREE',
    limit: int = 0
) -> List[Dict[str, Any]]:
    """
    Búsqueda personalizada en LDAP con filtro y scope específicos.

    Args:
        filter_query: Filtro LDAP personalizado
        attributes: Lista de atributos a retornar
        base_dn: Base DN para búsqueda
        scope: Alcance de búsqueda ('BASE', 'LEVEL', 'SUBTREE')
        limit: Límite de resultados

    Returns:
        Lista de diccionarios con resultados

    Example:
        >>> # Buscar computadoras
        >>> computers = search_custom('(objectClass=computer)')
        >>>
        >>> # Buscar objetos modificados recientemente
        >>> recent = search_custom(
        ...     filter_query='(whenChanged>=20240101000000.0Z)',
        ...     attributes=['cn', 'whenChanged']
        ... )
        >>>
        >>> # Buscar con scope específico
        >>> results = search_custom(
        ...     filter_query='(objectClass=*)',
        ...     scope='LEVEL'
        ... )
    """
    conn = None
    try:
        from ldap3 import BASE, LEVEL, SUBTREE

        conn = get_ldap_connection(base_dn=base_dn)

        # Determinar scope
        scope_map = {
            'BASE': BASE,
            'LEVEL': LEVEL,
            'SUBTREE': SUBTREE
        }
        search_scope = scope_map.get(scope.upper(), SUBTREE)

        # Configurar búsqueda
        search_attrs = attributes or ['*']
        search_base = base_dn or conn.server.info.naming_contexts[0]

        # Ejecutar búsqueda
        conn.search(
            search_base=search_base,
            search_filter=filter_query,
            search_scope=search_scope,
            attributes=search_attrs,
            size_limit=limit
        )

        # Convertir resultados
        results = []
        for entry in conn.entries:
            entry_dict = {'dn': entry.entry_dn}
            for attr in entry.entry_attributes:
                value = entry[attr].value
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                entry_dict[attr] = value
            results.append(entry_dict)

        return results

    except LDAPException as e:
        raise Exception(f"Error en búsqueda personalizada: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def find_user_by_username(
    username: str,
    username_attr: str = 'sAMAccountName',
    attributes: Optional[List[str]] = None,
    base_dn: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Busca un usuario específico por nombre de usuario.

    Args:
        username: Nombre de usuario a buscar
        username_attr: Atributo de username (default: 'sAMAccountName')
        attributes: Atributos a retornar
        base_dn: Base DN para búsqueda

    Returns:
        Dict con información del usuario, o None si no se encuentra

    Example:
        >>> user = find_user_by_username('jperez')
        >>> if user:
        ...     print(f"Nombre: {user['cn']}")
        ...     print(f"Email: {user['mail']}")
        ...     print(f"DN: {user['dn']}")
    """
    filter_query = f'({username_attr}={username})'
    results = search_users(
        filter_query=filter_query,
        attributes=attributes,
        base_dn=base_dn,
        limit=1
    )

    return results[0] if results else None


def find_group_by_name(
    group_name: str,
    attributes: Optional[List[str]] = None,
    base_dn: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Busca un grupo específico por nombre.

    Args:
        group_name: Nombre del grupo
        attributes: Atributos a retornar
        base_dn: Base DN para búsqueda

    Returns:
        Dict con información del grupo, o None si no se encuentra

    Example:
        >>> group = find_group_by_name('Administradores')
        >>> if group:
        ...     print(f"DN: {group['dn']}")
        ...     print(f"Miembros: {len(group.get('member', []))}")
    """
    filter_query = f'(cn={group_name})'
    results = search_groups(
        filter_query=filter_query,
        attributes=attributes,
        base_dn=base_dn,
        limit=1
    )

    return results[0] if results else None


def get_user_groups(
    username: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> List[str]:
    """
    Obtiene lista de grupos a los que pertenece un usuario.

    Args:
        username: Nombre de usuario
        username_attr: Atributo de username
        base_dn: Base DN para búsqueda

    Returns:
        Lista de DNs de grupos

    Example:
        >>> groups = get_user_groups('jperez')
        >>> for group_dn in groups:
        ...     print(group_dn)
    """
    user = find_user_by_username(
        username,
        username_attr=username_attr,
        attributes=['memberOf'],
        base_dn=base_dn
    )

    if not user:
        return []

    member_of = user.get('memberOf', [])

    # Asegurar que sea lista
    if not isinstance(member_of, list):
        member_of = [member_of]

    return member_of


def get_group_members(
    group_name: str,
    base_dn: Optional[str] = None
) -> List[str]:
    """
    Obtiene lista de miembros de un grupo.

    Args:
        group_name: Nombre del grupo
        base_dn: Base DN para búsqueda

    Returns:
        Lista de DNs de miembros

    Example:
        >>> members = get_group_members('Administradores')
        >>> for member_dn in members:
        ...     print(member_dn)
    """
    group = find_group_by_name(
        group_name,
        attributes=['member'],
        base_dn=base_dn
    )

    if not group:
        return []

    members = group.get('member', [])

    # Asegurar que sea lista
    if not isinstance(members, list):
        members = [members]

    return members
