"""
Funciones de gestión de Unidades Organizativas (OUs) en LDAP/Active Directory.

Este módulo proporciona funciones CRUD para gestionar OUs.

⚠️ ADVERTENCIA: Las operaciones de modificación requieren permisos de administrador.
"""
from typing import Optional, List, Dict, Any
from ldap3.core.exceptions import LDAPException
from ldap3 import MODIFY_REPLACE
from .ldap_connection import get_ldap_connection, close_ldap_connection


def create_ou(
    ou_name: str,
    description: Optional[str] = None,
    parent_ou: Optional[str] = None,
    base_dn: Optional[str] = None
) -> bool:
    """
    Crea una nueva Unidad Organizativa (OU).

    ⚠️ Requiere permisos de administrador.

    Args:
        ou_name: Nombre de la OU
        description: Descripción de la OU
        parent_ou: OU padre donde crear esta OU (ej: 'OU=Departamentos')
        base_dn: Base DN

    Returns:
        True si OU creada exitosamente

    Example:
        >>> # Crear OU en raíz
        >>> create_ou('Empleados', description='Todos los empleados')
        True
        >>>
        >>> # Crear OU anidada
        >>> create_ou('Ventas', parent_ou='OU=Empleados', description='Equipo de ventas')
        True
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Construir DN de la OU
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]

        if parent_ou:
            ou_dn = f'OU={ou_name},{parent_ou},{ldap_base_dn}'
        else:
            ou_dn = f'OU={ou_name},{ldap_base_dn}'

        # Atributos de la OU
        object_class = ['top', 'organizationalUnit']

        attributes = {
            'ou': ou_name
        }

        if description:
            attributes['description'] = description

        # Crear OU
        success = conn.add(ou_dn, object_class, attributes)

        if not success:
            raise LDAPException(f"Error creando OU: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error creando OU: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def delete_ou(
    ou_name: str,
    parent_ou: Optional[str] = None,
    base_dn: Optional[str] = None,
    recursive: bool = False
) -> bool:
    """
    Elimina una Unidad Organizativa.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.
    ⚠️ Si recursive=True, elimina TODOS los objetos dentro de la OU.
    ⚠️ Requiere permisos de administrador.

    Args:
        ou_name: Nombre de la OU
        parent_ou: OU padre (opcional)
        base_dn: Base DN
        recursive: Si True, elimina recursivamente todos los objetos (default: False)

    Returns:
        True si eliminación exitosa

    Example:
        >>> # Eliminar OU vacía
        >>> delete_ou('VentasTemp')
        True
        >>>
        >>> # Eliminar OU con todo su contenido
        >>> delete_ou('Temporal', recursive=True)
        True
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Construir DN de la OU
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]

        if parent_ou:
            ou_dn = f'OU={ou_name},{parent_ou},{ldap_base_dn}'
        else:
            ou_dn = f'OU={ou_name},{ldap_base_dn}'

        if recursive:
            # Eliminar recursivamente (requiere control de árbol de eliminación)
            from ldap3 import SUBTREE

            # Buscar todos los objetos dentro de la OU
            conn.search(
                search_base=ou_dn,
                search_filter='(objectClass=*)',
                search_scope=SUBTREE,
                attributes=['objectClass']
            )

            # Eliminar objetos en orden inverso (de hojas a raíz)
            dns_to_delete = [entry.entry_dn for entry in conn.entries]
            dns_to_delete.reverse()

            for dn in dns_to_delete:
                if dn != ou_dn:  # No eliminar la OU todavía
                    conn.delete(dn)

        # Eliminar la OU
        success = conn.delete(ou_dn)

        if not success:
            raise LDAPException(f"Error eliminando OU: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error eliminando OU: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def update_ou(
    ou_name: str,
    new_description: Optional[str] = None,
    new_name: Optional[str] = None,
    parent_ou: Optional[str] = None,
    base_dn: Optional[str] = None
) -> bool:
    """
    Actualiza atributos de una OU.

    ⚠️ Requiere permisos de administrador.

    Args:
        ou_name: Nombre actual de la OU
        new_description: Nueva descripción
        new_name: Nuevo nombre de la OU
        parent_ou: OU padre (si aplica)
        base_dn: Base DN

    Returns:
        True si actualización exitosa

    Example:
        >>> # Cambiar descripción
        >>> update_ou('Ventas', new_description='Departamento de ventas y marketing')
        True
        >>>
        >>> # Renombrar OU
        >>> update_ou('Marketing', new_name='Mercadotecnia')
        True
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Construir DN actual
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]

        if parent_ou:
            ou_dn = f'OU={ou_name},{parent_ou},{ldap_base_dn}'
        else:
            ou_dn = f'OU={ou_name},{ldap_base_dn}'

        # Actualizar descripción
        if new_description:
            changes = {'description': [(MODIFY_REPLACE, [new_description])]}
            success = conn.modify(ou_dn, changes)
            if not success:
                raise LDAPException(f"Error actualizando descripción: {conn.result}")

        # Renombrar OU
        if new_name:
            success = conn.modify_dn(ou_dn, f'OU={new_name}')
            if not success:
                raise LDAPException(f"Error renombrando OU: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error actualizando OU: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def move_ou(
    ou_name: str,
    new_parent_ou: str,
    current_parent_ou: Optional[str] = None,
    base_dn: Optional[str] = None
) -> bool:
    """
    Mueve una OU a una nueva ubicación en el árbol.

    ⚠️ Requiere permisos de administrador.

    Args:
        ou_name: Nombre de la OU a mover
        new_parent_ou: Nueva OU padre (ej: 'OU=Departamentos')
        current_parent_ou: OU padre actual (opcional)
        base_dn: Base DN

    Returns:
        True si movimiento exitoso

    Example:
        >>> move_ou('Ventas', 'OU=RegionNorte,OU=Empleados')
        True
    """
    conn = None
    try:
        conn = get_ldap_connection(base_dn=base_dn)

        # Construir DN actual
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]

        if current_parent_ou:
            current_dn = f'OU={ou_name},{current_parent_ou},{ldap_base_dn}'
        else:
            current_dn = f'OU={ou_name},{ldap_base_dn}'

        # Mover OU
        success = conn.modify_dn(
            current_dn,
            f'OU={ou_name}',
            new_superior=f'{new_parent_ou},{ldap_base_dn}'
        )

        if not success:
            raise LDAPException(f"Error moviendo OU: {conn.result}")

        return True

    except LDAPException as e:
        raise Exception(f"Error moviendo OU: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def list_ou_contents(
    ou_name: str,
    parent_ou: Optional[str] = None,
    base_dn: Optional[str] = None,
    object_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Lista el contenido de una OU.

    Args:
        ou_name: Nombre de la OU
        parent_ou: OU padre (opcional)
        base_dn: Base DN
        object_type: Filtrar por tipo ('user', 'group', 'organizationalUnit', o None para todos)

    Returns:
        Lista de diccionarios con objetos dentro de la OU

    Example:
        >>> # Listar todo el contenido
        >>> contents = list_ou_contents('Empleados')
        >>>
        >>> # Listar solo usuarios
        >>> users = list_ou_contents('Empleados', object_type='user')
        >>>
        >>> # Listar solo grupos
        >>> groups = list_ou_contents('Empleados', object_type='group')
    """
    conn = None
    try:
        from ldap3 import LEVEL

        conn = get_ldap_connection(base_dn=base_dn)

        # Construir DN de la OU
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]

        if parent_ou:
            ou_dn = f'OU={ou_name},{parent_ou},{ldap_base_dn}'
        else:
            ou_dn = f'OU={ou_name},{ldap_base_dn}'

        # Determinar filtro
        if object_type:
            if object_type.lower() == 'user':
                search_filter = '(objectClass=user)'
            elif object_type.lower() == 'group':
                search_filter = '(objectClass=group)'
            elif object_type.lower() == 'organizationalunit':
                search_filter = '(objectClass=organizationalUnit)'
            else:
                search_filter = f'(objectClass={object_type})'
        else:
            search_filter = '(objectClass=*)'

        # Buscar con scope LEVEL (solo hijos directos, no recursivo)
        conn.search(
            search_base=ou_dn,
            search_filter=search_filter,
            search_scope=LEVEL,
            attributes=['*']
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
        raise Exception(f"Error listando contenido de OU: {str(e)}")
    finally:
        if conn:
            close_ldap_connection(conn)


def ou_exists(
    ou_name: str,
    parent_ou: Optional[str] = None,
    base_dn: Optional[str] = None
) -> bool:
    """
    Verifica si una OU existe en el directorio.

    Args:
        ou_name: Nombre de la OU
        parent_ou: OU padre (opcional)
        base_dn: Base DN

    Returns:
        True si la OU existe

    Example:
        >>> if ou_exists('Empleados'):
        ...     print("La OU existe")
    """
    conn = None
    try:
        from ldap3 import BASE

        conn = get_ldap_connection(base_dn=base_dn)

        # Construir DN de la OU
        ldap_base_dn = base_dn or conn.server.info.naming_contexts[0]

        if parent_ou:
            ou_dn = f'OU={ou_name},{parent_ou},{ldap_base_dn}'
        else:
            ou_dn = f'OU={ou_name},{ldap_base_dn}'

        # Buscar con scope BASE (solo el objeto específico)
        conn.search(
            search_base=ou_dn,
            search_filter='(objectClass=organizationalUnit)',
            search_scope=BASE,
            attributes=['ou']
        )

        return len(conn.entries) > 0

    except LDAPException:
        return False
    finally:
        if conn:
            close_ldap_connection(conn)


def get_ou_tree(
    base_dn: Optional[str] = None,
    max_depth: int = 10
) -> Dict[str, Any]:
    """
    Obtiene el árbol completo de OUs en forma jerárquica.

    Args:
        base_dn: Base DN
        max_depth: Profundidad máxima del árbol (default: 10)

    Returns:
        Dict representando el árbol de OUs

    Example:
        >>> tree = get_ou_tree()
        >>> import json
        >>> print(json.dumps(tree, indent=2))
    """
    from .ldap_search import search_organizational_units

    try:
        # Buscar todas las OUs
        all_ous = search_organizational_units(base_dn=base_dn)

        # Construir árbol jerárquico
        tree = {
            'dn': base_dn,
            'ou': 'ROOT',
            'children': []
        }

        def add_to_tree(node, ou_data):
            """Agrega una OU al árbol en la posición correcta."""
            ou_dn = ou_data['dn']

            # Verificar si es hijo directo
            if base_dn and ou_dn.endswith(f',{node["dn"]}'):
                # Crear nodo para esta OU
                new_node = {
                    'dn': ou_dn,
                    'ou': ou_data.get('ou', ''),
                    'description': ou_data.get('description', ''),
                    'children': []
                }
                node['children'].append(new_node)
                return True

            # Buscar recursivamente en hijos
            for child in node['children']:
                if add_to_tree(child, ou_data):
                    return True

            return False

        # Ordenar OUs por profundidad (de raíz a hojas)
        all_ous.sort(key=lambda x: x['dn'].count(','))

        # Agregar cada OU al árbol
        for ou in all_ous:
            add_to_tree(tree, ou)

        return tree

    except Exception as e:
        raise Exception(f"Error obteniendo árbol de OUs: {str(e)}")
