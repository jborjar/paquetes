"""
Funciones de gestión de usuarios en LDAP/Active Directory.

Este módulo proporciona funciones CRUD (Create, Read, Update, Delete)
para usuarios en el directorio LDAP.

⚠️ ADVERTENCIA: Las operaciones de modificación requieren permisos de administrador.
"""
from typing import Dict, Optional, List, Any
from ldap3.core.exceptions import LDAPException
from ldap3 import MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from .ldap_connection import get_ldap_connection, close_ldap_connection


def create_user(
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    email: Optional[str] = None,
    ou: Optional[str] = None,
    base_dn: Optional[str] = None,
    additional_attributes: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Crea un nuevo usuario en LDAP/Active Directory.

    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario (sAMAccountName)
        password: Contraseña inicial
        first_name: Nombre
        last_name: Apellido
        email: Email (opcional)
        ou: Unidad organizativa donde crear el usuario (ej: 'OU=Users')
        base_dn: Base DN (opcional)
        additional_attributes: Atributos adicionales a establecer

    Returns:
        True si usuario creado exitosamente, False en caso contrario

    Example:
        >>> create_user(
        ...     username='jperez',
        ...     password='Password123!',
        ...     first_name='Juan',
        ...     last_name='Pérez',
        ...     email='jperez@empresa.com',
        ...     ou='OU=Empleados'
        ... )
        True
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Construir DN del usuario
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]
        user_ou = ou if ou else 'CN=Users'
        user_dn = f'CN={first_name} {last_name},{user_ou},{ldap_base_dn}'

        # Atributos básicos del usuario
        object_class = ['top', 'person', 'organizationalPerson', 'user']

        attributes = {
            'cn': f'{first_name} {last_name}',
            'sAMAccountName': username,
            'givenName': first_name,
            'sn': last_name,
            'displayName': f'{first_name} {last_name}',
            'userPrincipalName': f'{username}@{ldap_base_dn.replace("DC=", "").replace(",", ".")}',
        }

        if email:
            attributes['mail'] = email

        # Agregar atributos adicionales
        if additional_attributes:
            attributes.update(additional_attributes)

        # Crear usuario
        success = conn.add(user_dn, object_class, attributes)

        if not success:
            raise LDAPException(f"Error creando usuario: {conn.result}")

        # Establecer contraseña (Active Directory)
        # Nota: La contraseña debe estar en formato UTF-16-LE y entre comillas
        password_value = f'"{password}"'.encode('utf-16-le')
        conn.modify(user_dn, {'unicodePwd': [(MODIFY_REPLACE, [password_value])]})

        # Habilitar cuenta (userAccountControl = 512 = cuenta normal habilitada)
        conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]})

        return True

    except LDAPException as e:
        raise Exception(f"Error creando usuario: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def update_user(
    username: str,
    attributes: Dict[str, Any],
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Actualiza atributos de un usuario existente.

    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario a actualizar
        attributes: Diccionario de atributos a actualizar
        username_attr: Atributo de username (default: 'sAMAccountName')
        base_dn: Base DN

    Returns:
        True si actualización exitosa, False en caso contrario

    Example:
        >>> # Actualizar email y teléfono
        >>> update_user('jperez', {
        ...     'mail': 'juan.perez@empresa.com',
        ...     'telephoneNumber': '+1234567890',
        ...     'title': 'Gerente de Ventas'
        ... })
        True
    """
    conn = None
    try:
        from .ldap_search import find_user_by_username

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar usuario para obtener DN
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            raise Exception(f"Usuario '{username}' no encontrado")

        user_dn = user['dn']

        # Construir cambios
        changes = {}
        for attr, value in attributes.items():
            changes[attr] = [(MODIFY_REPLACE, [value])]

        # Aplicar cambios
        success = conn.modify(user_dn, changes)

        if not success:
            raise LDAPException(f"Error actualizando usuario: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error actualizando usuario: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def delete_user(
    username: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Elimina un usuario del directorio LDAP.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.
    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario a eliminar
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si eliminación exitosa, False en caso contrario

    Example:
        >>> delete_user('jperez')
        True
    """
    conn = None
    try:
        from .ldap_search import find_user_by_username

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar usuario
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            raise Exception(f"Usuario '{username}' no encontrado")

        user_dn = user['dn']

        # Eliminar usuario
        success = conn.delete(user_dn)

        if not success:
            raise LDAPException(f"Error eliminando usuario: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error eliminando usuario: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def disable_user(
    username: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Deshabilita una cuenta de usuario (sin eliminarla).

    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si deshabilitación exitosa

    Example:
        >>> disable_user('jperez')
        True
    """
    conn = None
    try:
        from .ldap_search import find_user_by_username

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar usuario
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            raise Exception(f"Usuario '{username}' no encontrado")

        user_dn = user['dn']

        # Deshabilitar (userAccountControl = 514 = cuenta deshabilitada)
        changes = {'userAccountControl': [(MODIFY_REPLACE, [514])]}
        success = conn.modify(user_dn, changes)

        if not success:
            raise LDAPException(f"Error deshabilitando usuario: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error deshabilitando usuario: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def enable_user(
    username: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Habilita una cuenta de usuario deshabilitada.

    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si habilitación exitosa

    Example:
        >>> enable_user('jperez')
        True
    """
    conn = None
    try:
        from .ldap_search import find_user_by_username

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar usuario
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            raise Exception(f"Usuario '{username}' no encontrado")

        user_dn = user['dn']

        # Habilitar (userAccountControl = 512 = cuenta habilitada)
        changes = {'userAccountControl': [(MODIFY_REPLACE, [512])]}
        success = conn.modify(user_dn, changes)

        if not success:
            raise LDAPException(f"Error habilitando usuario: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error habilitando usuario: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def change_user_password(
    username: str,
    new_password: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Cambia la contraseña de un usuario.

    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario
        new_password: Nueva contraseña
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si cambio exitoso

    Example:
        >>> change_user_password('jperez', 'NewPassword123!')
        True
    """
    conn = None
    try:
        from .ldap_search import find_user_by_username

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar usuario
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            raise Exception(f"Usuario '{username}' no encontrado")

        user_dn = user['dn']

        # Cambiar contraseña (formato UTF-16-LE con comillas)
        password_value = f'"{new_password}"'.encode('utf-16-le')
        changes = {'unicodePwd': [(MODIFY_REPLACE, [password_value])]}

        success = conn.modify(user_dn, changes)

        if not success:
            raise LDAPException(f"Error cambiando contraseña: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error cambiando contraseña: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def move_user(
    username: str,
    new_ou: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Mueve un usuario a una nueva unidad organizativa.

    ⚠️ Requiere permisos de administrador.

    Args:
        username: Nombre de usuario
        new_ou: Nueva OU (ej: 'OU=Ventas,OU=Empleados')
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si movimiento exitoso

    Example:
        >>> move_user('jperez', 'OU=Gerentes,OU=Empleados')
        True
    """
    conn = None
    try:
        from .ldap_search import find_user_by_username

        conn = get_ldap_connection(base_dn=base_dn)

        # Buscar usuario
        user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
        if not user:
            raise Exception(f"Usuario '{username}' no encontrado")

        user_dn = user['dn']

        # Obtener CN del usuario
        cn = user.get('cn', f"{user.get('givenName', '')} {user.get('sn', '')}".strip())

        # Construir nuevo DN
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]
        new_dn = f'CN={cn},{new_ou},{ldap_base_dn}'

        # Mover usuario
        success = conn.modify_dn(user_dn, f'CN={cn}', new_superior=f'{new_ou},{ldap_base_dn}')

        if not success:
            raise LDAPException(f"Error moviendo usuario: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error moviendo usuario: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def user_exists(
    username: str,
    username_attr: str = 'sAMAccountName',
    base_dn: Optional[str] = None
) -> bool:
    """
    Verifica si un usuario existe en el directorio.

    Args:
        username: Nombre de usuario
        username_attr: Atributo de username
        base_dn: Base DN

    Returns:
        True si el usuario existe, False en caso contrario

    Example:
        >>> if user_exists('jperez'):
        ...     print("El usuario existe")
    """
    from .ldap_search import find_user_by_username

    user = find_user_by_username(username, username_attr=username_attr, base_dn=base_dn)
    return user is not None
