#!/usr/bin/env python3
"""Test de conexión LDAP desde software/app."""
import os
import sys

# Cargar .env
env_file = '../../infraestructura/.env'
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Importar paquete LDAP
from paquetes.ldap import test_ldap_connection, search_users

print("=" * 60)
print("PRUEBA DE CONEXIÓN LDAP")
print("=" * 60)
print(f"Servidor: {os.getenv('LDAP_SERVER')}")
print(f"Puerto: {os.getenv('LDAP_PORT')}")
print(f"SSL: {os.getenv('LDAP_USE_SSL')}")
print(f"Base DN: {os.getenv('LDAP_BASE_DN')}")
print()

# Probar conexión
print("Probando conexión...")
result = test_ldap_connection()

if result['success']:
    print("✓ CONEXIÓN EXITOSA")
    print(f"  Servidor: {result['server']}")
    print(f"  Puerto: {result['port']}")
    print(f"  SSL: {result['use_ssl']}")

    if result.get('info'):
        print("\nInformación del servidor:")
        info = result['info']
        for key, value in info.items():
            print(f"  {key}: {value}")

    # Intentar buscar usuarios
    print("\n" + "=" * 60)
    print("BÚSQUEDA DE USUARIOS")
    print("=" * 60)
    print("Buscando usuarios en el directorio...")

    try:
        users = search_users(limit=5)
        if users:
            print(f"✓ Se encontraron {len(users)} usuarios:")
            for user in users:
                cn = user.get('cn', ['N/A'])[0] if isinstance(user.get('cn'), list) else user.get('cn', 'N/A')
                sam = user.get('sAMAccountName', ['N/A'])[0] if isinstance(user.get('sAMAccountName'), list) else user.get('sAMAccountName', 'N/A')
                print(f"  - {cn} ({sam})")
        else:
            print("⚠️  No se encontraron usuarios")
    except Exception as e:
        print(f"✗ Error al buscar usuarios: {e}")

else:
    print("✗ ERROR DE CONEXIÓN")
    print(f"  Error: {result.get('error', 'Error desconocido')}")
    if result.get('details'):
        print(f"  Detalles: {result['details']}")
    sys.exit(1)

print("\n" + "=" * 60)
print("PRUEBA COMPLETADA")
print("=" * 60)
