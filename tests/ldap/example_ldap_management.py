"""
Ejemplo de gestión (CRUD) con el módulo LDAP.

Este script muestra operaciones de administración:
- Creación de OUs, usuarios y grupos
- Gestión de membresías
- Modificación de atributos
- Eliminación de objetos

⚠️ ADVERTENCIA: Este script realiza modificaciones en el directorio LDAP.
   Solo ejecutar en ambiente de pruebas.

IMPORTANTE: Requiere permisos de administrador y variables de entorno configuradas.
"""
import os
import sys

# Agregar path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ldap import (
    # OUs
    create_ou,
    list_ou_contents,
    ou_exists,
    delete_ou,
    # Usuarios
    create_user,
    update_user,
    disable_user,
    enable_user,
    user_exists,
    delete_user,
    # Grupos
    create_group,
    add_user_to_group,
    remove_user_from_group,
    list_group_members,
    group_exists,
    delete_group
)


def demo_ou_management():
    """Demo de gestión de OUs."""
    print("\n" + "=" * 60)
    print("DEMO: Gestión de Unidades Organizativas (OUs)")
    print("=" * 60)

    # Crear OU principal
    print("\n1. Crear OU 'TestDemo'...")
    try:
        if not ou_exists('TestDemo'):
            create_ou('TestDemo', description='OU de pruebas para demo')
            print("✓ OU 'TestDemo' creada")
        else:
            print("○ OU 'TestDemo' ya existe")

        # Crear sub-OUs
        print("\n2. Crear sub-OUs...")
        sub_ous = [
            ('Usuarios', 'Usuarios de prueba'),
            ('Grupos', 'Grupos de prueba')
        ]

        for ou_name, desc in sub_ous:
            if not ou_exists(ou_name, parent_ou='OU=TestDemo'):
                create_ou(ou_name, parent_ou='OU=TestDemo', description=desc)
                print(f"✓ OU '{ou_name}' creada")
            else:
                print(f"○ OU '{ou_name}' ya existe")

        print("\n✓ Estructura de OUs creada exitosamente")

    except Exception as e:
        print(f"✗ Error: {e}")


def demo_user_management():
    """Demo de gestión de usuarios."""
    print("\n" + "=" * 60)
    print("DEMO: Gestión de Usuarios")
    print("=" * 60)

    # Crear usuario
    print("\n1. Crear usuario de prueba...")
    username = 'test.demo'

    try:
        if not user_exists(username):
            create_user(
                username=username,
                password='TestDemo123!',
                first_name='Test',
                last_name='Demo',
                email='test.demo@empresa.com',
                ou='OU=Usuarios,OU=TestDemo'
            )
            print(f"✓ Usuario '{username}' creado")
        else:
            print(f"○ Usuario '{username}' ya existe")

        # Actualizar atributos
        print("\n2. Actualizar atributos del usuario...")
        update_user(username, {
            'telephoneNumber': '+1234567890',
            'title': 'Usuario de Prueba'
        })
        print(f"✓ Atributos actualizados")

        # Deshabilitar
        print("\n3. Deshabilitar usuario...")
        disable_user(username)
        print(f"✓ Usuario deshabilitado")

        # Habilitar
        print("\n4. Habilitar usuario...")
        enable_user(username)
        print(f"✓ Usuario habilitado")

        print("\n✓ Gestión de usuario completada")

    except Exception as e:
        print(f"✗ Error: {e}")


def demo_group_management():
    """Demo de gestión de grupos."""
    print("\n" + "=" * 60)
    print("DEMO: Gestión de Grupos y Membresías")
    print("=" * 60)

    group_name = 'TestDemoGroup'
    username = 'test.demo'

    try:
        # Crear grupo
        print("\n1. Crear grupo de prueba...")
        if not group_exists(group_name):
            create_group(
                group_name=group_name,
                description='Grupo de prueba para demo',
                ou='OU=Grupos,OU=TestDemo'
            )
            print(f"✓ Grupo '{group_name}' creado")
        else:
            print(f"○ Grupo '{group_name}' ya existe")

        # Agregar usuario al grupo
        print(f"\n2. Agregar usuario '{username}' al grupo...")
        if user_exists(username):
            add_user_to_group(username, group_name)
            print(f"✓ Usuario agregado al grupo")

            # Listar miembros
            print(f"\n3. Listar miembros del grupo...")
            members = list_group_members(group_name, detailed=True)
            print(f"✓ El grupo tiene {len(members)} miembro(s):")
            for member in members:
                print(f"  - {member.get('cn')} ({member.get('sAMAccountName')})")

            # Remover usuario
            print(f"\n4. Remover usuario del grupo...")
            remove_user_from_group(username, group_name)
            print(f"✓ Usuario removido del grupo")
        else:
            print(f"✗ Usuario '{username}' no existe (ejecutar demo de usuarios primero)")

        print("\n✓ Gestión de grupo completada")

    except Exception as e:
        print(f"✗ Error: {e}")


def demo_cleanup():
    """Limpia los objetos creados en las demos."""
    print("\n" + "=" * 60)
    print("CLEANUP: Eliminando objetos de prueba")
    print("=" * 60)

    confirm = input("\n¿Desea eliminar todos los objetos de prueba? (s/n): ")
    if confirm.lower() != 's':
        print("Operación cancelada")
        return

    try:
        # Eliminar grupo
        print("\n1. Eliminar grupo...")
        if group_exists('TestDemoGroup'):
            delete_group('TestDemoGroup')
            print("✓ Grupo eliminado")

        # Eliminar usuario
        print("\n2. Eliminar usuario...")
        if user_exists('test.demo'):
            delete_user('test.demo')
            print("✓ Usuario eliminado")

        # Eliminar OUs (recursivo)
        print("\n3. Eliminar OUs...")
        if ou_exists('TestDemo'):
            delete_ou('TestDemo', recursive=True)
            print("✓ OU 'TestDemo' y todo su contenido eliminados")

        print("\n✓ Cleanup completado exitosamente")

    except Exception as e:
        print(f"✗ Error durante cleanup: {e}")


def demo_complete_workflow():
    """Ejecuta un flujo completo de trabajo."""
    print("\n" + "=" * 60)
    print("DEMO: Flujo Completo de Trabajo")
    print("=" * 60)

    print("""
Este demo ejecutará:
1. Crear estructura de OUs (TestDemo/Usuarios, TestDemo/Grupos)
2. Crear usuario de prueba (test.demo)
3. Crear grupo de prueba (TestDemoGroup)
4. Agregar usuario al grupo
5. Listar membresías
6. Cleanup (eliminar todo)

⚠️ Se realizarán modificaciones en el directorio LDAP.
    """)

    confirm = input("¿Continuar? (s/n): ")
    if confirm.lower() != 's':
        print("Demo cancelado")
        return

    try:
        # Ejecutar demos en orden
        demo_ou_management()
        demo_user_management()
        demo_group_management()

        print("\n" + "=" * 60)
        print("FLUJO COMPLETO EXITOSO")
        print("=" * 60)

        # Preguntar por cleanup
        demo_cleanup()

    except Exception as e:
        print(f"\n✗ Error en flujo completo: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 8 + "EJEMPLO GESTIÓN - MÓDULO LDAP" + " " * 20 + "║")
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

    print("⚠️  ADVERTENCIA:")
    print("  Este script realiza modificaciones en el directorio LDAP.")
    print("  Solo ejecutar en ambiente de pruebas con permisos de administrador.")
    print()

    # Menú de opciones
    while True:
        print("\n" + "-" * 60)
        print("OPCIONES:")
        print("  1. Demo: Gestión de OUs")
        print("  2. Demo: Gestión de Usuarios")
        print("  3. Demo: Gestión de Grupos")
        print("  4. Demo: Flujo Completo (crea y limpia todo)")
        print("  5. Cleanup: Eliminar objetos de prueba")
        print("  0. Salir")
        print("-" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == '1':
            demo_ou_management()
        elif opcion == '2':
            demo_user_management()
        elif opcion == '3':
            demo_group_management()
        elif opcion == '4':
            demo_complete_workflow()
        elif opcion == '5':
            demo_cleanup()
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
