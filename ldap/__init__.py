"""
Módulo LDAP - Operaciones completas para LDAP/Active Directory.

Este módulo proporciona funciones organizadas por categorías:
- CONNECTION: Gestión de conexiones
- AUTH: Autenticación y validación de credenciales
- SEARCH: Búsqueda de usuarios, grupos y OUs
- USERS: Gestión CRUD de usuarios
- GROUPS: Gestión CRUD de grupos y membresías
- OUS: Gestión CRUD de unidades organizativas

Requiere: pip install ldap3
"""

# CONNECTION - Gestión de conexiones
from .ldap_connection import (
    get_ldap_connection,
    test_ldap_connection,
    close_ldap_connection
)

# AUTH - Autenticación
from .ldap_auth import (
    authenticate_user,
    get_user_info,
    verify_credentials
)

# SEARCH - Búsqueda
from .ldap_search import (
    search_users,
    search_groups,
    search_organizational_units,
    search_custom,
    find_user_by_username,
    find_group_by_name,
    get_user_groups,
    get_group_members
)

# USERS - Gestión de usuarios
from .ldap_users import (
    create_user,
    update_user,
    delete_user,
    disable_user,
    enable_user,
    change_user_password,
    move_user,
    user_exists
)

# GROUPS - Gestión de grupos
from .ldap_groups import (
    create_group,
    delete_group,
    add_user_to_group,
    remove_user_from_group,
    is_user_in_group,
    list_group_members,
    update_group,
    group_exists
)

# OUS - Gestión de unidades organizativas
from .ldap_ous import (
    create_ou,
    delete_ou,
    update_ou,
    move_ou,
    list_ou_contents,
    ou_exists,
    get_ou_tree
)

__all__ = [
    # === CONNECTION - Gestión de conexiones ===
    "get_ldap_connection",
    "test_ldap_connection",
    "close_ldap_connection",

    # === AUTH - Autenticación ===
    "authenticate_user",
    "get_user_info",
    "verify_credentials",

    # === SEARCH - Búsqueda ===
    "search_users",
    "search_groups",
    "search_organizational_units",
    "search_custom",
    "find_user_by_username",
    "find_group_by_name",
    "get_user_groups",
    "get_group_members",

    # === USERS - Gestión de usuarios ===
    "create_user",
    "update_user",
    "delete_user",
    "disable_user",
    "enable_user",
    "change_user_password",
    "move_user",
    "user_exists",

    # === GROUPS - Gestión de grupos ===
    "create_group",
    "delete_group",
    "add_user_to_group",
    "remove_user_from_group",
    "is_user_in_group",
    "list_group_members",
    "update_group",
    "group_exists",

    # === OUS - Gestión de unidades organizativas ===
    "create_ou",
    "delete_ou",
    "update_ou",
    "move_ou",
    "list_ou_contents",
    "ou_exists",
    "get_ou_tree"
]
