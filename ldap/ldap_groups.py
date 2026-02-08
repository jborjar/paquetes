"""
Funciones de gestión de grupos en LDAP/Active Directory.

Este módulo proporciona funciones CRUD para grupos y gestión de membresías.

⚠️ ADVERTENCIA: Las operaciones de modificación requieren permisos de administrador.
"""
from typing import Optional, List
from ldap3.core.exceptions import LDAPException
from ldap3 import MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from .ldap_connection import get_ldap_connection, close_ldap_connection


def create_group(
    group_name: str,
    description: Optional[str] = None,
    ou: Optional[str] = None,
    base_dn: Optional[str] = None,
    group_type: str = 'security'
) -> bool:
    """
    Crea un nuevo grupo en LDAP/Active Directory.

    ⚠️ Requiere permisos de administrador.

    Args:
        group_name: Nombre del grupo
        description: Descripción del grupo
        ou: Unidad organizativa donde crear el grupo (ej: 'OU=Grupos')
        base_dn: Base DN
        group_type: Tipo de grupo ('security' o 'distribution')

    Returns:
        True si grupo creado exitosamente

    Example:
        >>> create_group(
        ...     group_name='Desarrolladores',
        ...     description='Equipo de desarrollo',
        ...     ou='OU=Grupos'
        ... )
        True
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Construir DN del grupo
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]
        group_ou = ou if ou else 'CN=Users'
        group_dn = f'CN={group_name},{group_ou},{ldap_base_dn}'

        # Atributos del grupo
        object_class = ['top', 'group']

        # Determinar groupType
        # -2147483646 = Global Security Group (más común)
        # -2147483644 = Domain Local Security Group
        # -2147483640 = Universal Security Group
        # 2 = Global Distribution Group
        # 4 = Domain Local Distribution Group
        # 8 = Universal Distribution Group
        group_type_value = -2147483646 if group_type == 'security' else 2

        attributes = {
            'cn': group_name,
            'sAMAccountName': group_name,
            'groupType': group_type_value
        }

        if description:
            attributes['description'] = description

        # Crear grupo
        success = conn.add(group_dn, object_class, attributes)

        if not success:
            raise LDAPException(f"Error creando grupo: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error creando grupo: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def delete_group(
    group_name: str,
    base_dn: Optional[str] = None
) -> bool:
    """
    Elimina un grupo del directorio LDAP.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.
    ⚠️ Requiere permisos de administrador.

    Args:
        group_name: Nombre del grupo a eliminar
        base_dn: Base DN

    Returns:
        True si eliminación exitosa

    Example:
        >>> delete_group('GrupoTemporal')
        True
    """
    conn = None
    try:
        from .ldap_search import find_group_by_name

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar grupo
        group = find_group_by_name(group_name, base_dn=base_dn)
        if not group:
            raise Exception(f"Grupo '{group_name}' no encontrado")

        group_dn = group['dn']

        # Eliminar grupo
        success = conn.delete(group_dn)

        if not success:
            raise LDAPException(f"Error eliminando grupo: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error eliminando grupo: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def add_user_to_group(
    username: str,
    group_name: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Agrega un usuario a un grupo.

    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario
        group_name: Nombre del grupo
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si operación exitosa

    Example:
        >>> add_user_to_group('jperez', 'Desarrolladores')
        True
    """
    conn = None
    try:
        from .ldap_search import find_user_by_username, find_group_by_name

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar usuario
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            raise Exception(f"Usuario '{username}' no encontrado")

        # Buscar grupo
        group = find_group_by_name(group_name, base_dn=base_dn)
        if not group:
            raise Exception(f"Grupo '{group_name}' no encontrado")

        user_dn = user['dn']
        group_dn = group['dn']

        # Agregar usuario al grupo
        changes = {'member': [(MODIFY_ADD, [user_dn])]}
        success = conn.modify(group_dn, changes)

        if not success:
            # Verificar si ya es miembro
            if 'entryAlreadyExists' in str(conn.result):
                return True  # Ya es miembro, considerar exitoso
            raise LDAPException(f"Error agregando usuario a grupo: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error agregando usuario a grupo: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def remove_user_from_group(
    username: str,
    group_name: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Remueve un usuario de un grupo.

    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario
        group_name: Nombre del grupo
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si operación exitosa

    Example:
        >>> remove_user_from_group('jperez', 'Desarrolladores')
        True
    """
    conn = None
    try:
        from .ldap_search import find_user_by_username, find_group_by_name

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar usuario
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            raise Exception(f"Usuario '{username}' no encontrado")

        # Buscar grupo
        group = find_group_by_name(group_name, base_dn=base_dn)
        if not group:
            raise Exception(f"Grupo '{group_name}' no encontrado")

        user_dn = user['dn']
        group_dn = group['dn']

        # Remover usuario del grupo
        changes = {'member': [(MODIFY_DELETE, [user_dn])]}
        success = conn.modify(group_dn, changes)

        if not success:
            raise LDAPException(f"Error removiendo usuario de grupo: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error removiendo usuario de grupo: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def is_user_in_group(
    username: str,
    group_name: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Verifica si un usuario es miembro de un grupo.

    Args:
        username: Nombre de usuario
        group_name: Nombre del grupo
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si el usuario es miembro del grupo

    Example:
        >>> if is_user_in_group('jperez', 'Administradores'):
        ...     print("El usuario es administrador")
    """
    try:
        from .ldap_search import find_user_by_username, find_group_by_name

        # Buscar usuario
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            return False

        # Buscar grupo
        group = find_group_by_name(group_name, base_dn=base_dn)
        if not group:
            return False

        user_dn = user['dn']
        group_members = group.get('member', [])

        # Asegurar que sea lista
        if not isinstance(group_members, list):
            group_members = [group_members]

        return user_dn in group_members

    except Exception:
        return False


def list_group_members(
    group_name: str,
    base_dn: Optional[str] = None,
    detailed: bool = False
) -> List:
    """
    Lista los miembros de un grupo.

    Args:
        group_name: Nombre del grupo
        base_dn: Base DN
        detailed: Si True, retorna info completa; si False, solo DNs

    Returns:
        Lista de DNs (detailed=False) o lista de dicts con info de usuarios (detailed=True)

    Example:
        >>> # Solo DNs
        >>> members = list_group_members('Desarrolladores')
        >>> for member_dn in members:
        ...     print(member_dn)
        >>>
        >>> # Información detallada
        >>> members = list_group_members('Desarrolladores', detailed=True)
        >>> for member in members:
        ...     print(f"{member['cn']} - {member['mail']}")
    """
    try:
        from .ldap_search import find_group_by_name, search_users

        # Buscar grupo
        group = find_group_by_name(group_name, base_dn=base_dn)
        if not group:
            return []

        members = group.get('member', [])

        # Asegurar que sea lista
        if not isinstance(members, list):
            members = [members] if members else []

        if not detailed:
            return members

        # Obtener información detallada de cada miembro
        detailed_members = []
        for member_dn in members:
            # Buscar usuario por DN
            users = search_users(
                filter_query=f'(distinguishedName={member_dn})',
                base_dn=base_dn,
                limit=1
            )
            if users:
                detailed_members.append(users[0])

        return detailed_members

    except Exception:
        return []


def update_group(
    group_name: str,
    description: Optional[str] = None,
    new_name: Optional[str] = None,
    base_dn: Optional[str] = None
) -> bool:
    """
    Actualiza atributos de un grupo.

    ⚠️ Requiere permisos de administrador.

    Args:
        group_name: Nombre del grupo actual
        description: Nueva descripción (opcional)
        new_name: Nuevo nombre del grupo (opcional)
        base_dn: Base DN

    Returns:
        True si actualización exitosa

    Example:
        >>> # Cambiar descripción
        >>> update_group('Desarrolladores', description='Equipo de desarrollo de software')
        True
        >>>
        >>> # Renombrar grupo
        >>> update_group('DevTeam', new_name='Desarrolladores')
        True
    """
    conn = None
    try:
        from .ldap_search import find_group_by_name

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar grupo
        group = find_group_by_name(group_name, base_dn=base_dn)
        if not group:
            raise Exception(f"Grupo '{group_name}' no encontrado")

        group_dn = group['dn']

        # Actualizar descripción
        if description:
            changes = {'description': [(MODIFY_REPLACE, [description])]}
            success = conn.modify(group_dn, changes)
            if not success:
                raise LDAPException(f"Error actualizando descripción: {conn.result}")

        # Renombrar grupo
        if new_name:
            success = conn.modify_dn(group_dn, f'CN={new_name}')
            if not success:
                raise LDAPException(f"Error renombrando grupo: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error actualizando grupo: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def group_exists(
    group_name: str,
    base_dn: Optional[str] = None
) -> bool:
    """
    Verifica si un grupo existe en el directorio.

    Args:
        group_name: Nombre del grupo
        base_dn: Base DN

    Returns:
        True si el grupo existe

    Example:
        >>> if group_exists('Administradores'):
        ...     print("El grupo existe")
    """
    from .ldap_search import find_group_by_name

    group = find_group_by_name(group_name, base_dn=base_dn)
    return group is not None
