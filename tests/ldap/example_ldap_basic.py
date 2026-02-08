"""
Ejemplo básico de uso del módulo LDAP.

Este script muestra las operaciones más comunes:
- Conexión y prueba
- Autenticación de usuarios
- Búsqueda de usuarios y grupos
- Consultas de información

IMPORTANTE: Configura las variables de entorno antes de ejecutar:
- LDAP_SERVER
- LDAP_BASE_DN
- LDAP_BIND_DN
- LDAP_BIND_PASSWORD
"""
import os
import sys

# Agregar path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ldap import (
    test_ldap_connection,
    authenticate_user,
    verify_credentials,
    search_users,
    search_groups,
    find_user_by_username,
    get_user_groups,
    get_group_members
)


def test_connection():
    """Prueba la conexión al servidor LDAP."""
    print("=" * 60)
    print("TEST: Conexión al servidor LDAP")
    print("=" * 60)

    result = test_ldap_connection()

    if result['success']:
        print("✓ Conexión exitosa")
        print(f"  Servidor: {result['info']['server']}:{result['info']['port']}")
        print(f"  SSL: {result['info']['ssl']}")
        print(f"  Versiones LDAP: {result['info']['version']}")
        print(f"  Naming Contexts: {result['info']['naming_contexts']}")
        return True
    else:
        print(f"✗ Error de conexión: {result['error']}")
        return False


def test_authentication():
    """Prueba autenticación de usuario."""
    print("\n" + "=" * 60)
    print("TEST: Autenticación de Usuario")
    print("=" * 60)

    # Solicitar credenciales
    username = input("Usuario a autenticar: ")
    password = input("Contraseña: ")

    # Autenticación simple
    print("\n1. Autenticación simple...")
    if authenticate_user(username, password):
        print(f"✓ Usuario '{username}' autenticado correctamente")
    else:
        print(f"✗ Autenticación fallida para '{username}'")
        return

    # Verificación detallada
    print("\n2. Verificación con detalles...")
    result = verify_credentials(username, password)
    if result['valid']:
        print(f"✓ Credenciales válidas")
        print(f"  DN: {result['dn']}")
    else:
        print(f"✗ {result['error']}")


def test_user_search():
    """Prueba búsqueda de usuarios."""
    print("\n" + "=" * 60)
    print("TEST: Búsqueda de Usuarios")
    print("=" * 60)

    # Buscar todos los usuarios (limitado a 10)
    print("\n1. Listando primeros 10 usuarios...")
    users = search_users(limit=10)

    if users:
        print(f"✓ Encontrados {len(users)} usuarios:")
        for user in users:
            cn = user.get('cn', 'N/A')
            mail = user.get('mail', 'N/A')
            sam = user.get('sAMAccountName', 'N/A')
            print(f"  - {cn} ({sam}) - {mail}")
    else:
        print("No se encontraron usuarios")

    # Buscar usuario específico
    print("\n2. Buscar usuario específico...")
    username = input("Nombre de usuario a buscar (sAMAccountName): ")

    user = find_user_by_username(username)
    if user:
        print(f"✓ Usuario encontrado:")
        print(f"  DN: {user['dn']}")
        print(f"  Nombre: {user.get('cn', 'N/A')}")
        print(f"  Email: {user.get('mail', 'N/A')}")
        print(f"  Teléfono: {user.get('telephoneNumber', 'N/A')}")

        # Mostrar grupos
        groups = user.get('memberOf', [])
        if not isinstance(groups, list):
            groups = [groups] if groups else []

        if groups:
            print(f"  Grupos ({len(groups)}):")
            for group in groups[:5]:  # Mostrar solo primeros 5
                print(f"    - {group}")
            if len(groups) > 5:
                print(f"    ... y {len(groups) - 5} más")
    else:
        print(f"✗ Usuario '{username}' no encontrado")


def test_group_search():
    """Prueba búsqueda de grupos."""
    print("\n" + "=" * 60)
    print("TEST: Búsqueda de Grupos")
    print("=" * 60)

    # Listar grupos
    print("\n1. Listando primeros 10 grupos...")
    groups = search_groups(limit=10)

    if groups:
        print(f"✓ Encontrados {len(groups)} grupos:")
        for group in groups:
            cn = group.get('cn', 'N/A')
            desc = group.get('description', 'Sin descripción')
            members = group.get('member', [])
            if not isinstance(members, list):
                members = [members] if members else []

            print(f"  - {cn}: {desc}")
            print(f"    Miembros: {len(members)}")
    else:
        print("No se encontraron grupos")

    # Buscar grupo y listar miembros
    print("\n2. Listar miembros de un grupo...")
    group_name = input("Nombre del grupo (cn): ")

    members_dns = get_group_members(group_name)
    if members_dns:
        print(f"✓ Grupo '{group_name}' tiene {len(members_dns)} miembros:")
        for member_dn in members_dns[:10]:  # Mostrar primeros 10
            print(f"  - {member_dn}")
        if len(members_dns) > 10:
            print(f"  ... y {len(members_dns) - 10} más")
    else:
        print(f"Grupo '{group_name}' no tiene miembros o no existe")


def main():
    """Función principal."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "EJEMPLO BÁSICO - MÓDULO LDAP" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Verificar variables de entorno
    required_vars = ['LDAP_SERVER', 'LDAP_BASE_DN', 'LDAP_BIND_DN', 'LDAP_BIND_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("⚠️  Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nConfigura estas variables antes de continuar.")
        return

    # Menú de opciones
    while True:
        print("\n" + "-" * 60)
        print("OPCIONES:")
        print("  1. Probar conexión")
        print("  2. Autenticar usuario")
        print("  3. Buscar usuarios")
        print("  4. Buscar grupos")
        print("  5. Ejecutar todos los tests")
        print("  0. Salir")
        print("-" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == '1':
            test_connection()
        elif opcion == '2':
            test_authentication()
        elif opcion == '3':
            test_user_search()
        elif opcion == '4':
            test_group_search()
        elif opcion == '5':
            if test_connection():
                test_authentication()
                test_user_search()
                test_group_search()
        elif opcion == '0':
            print("\n¡Hasta luego!")
            break
        else:
            print("Opción no válida")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
