#!/usr/bin/env python3
"""Test de conexión LDAP con debug."""
import os
import sys
import socket

# Cargar .env
env_file = '../../infraestructura/.env'
print("1. Cargando variables de entorno...")
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    print("   ✓ Variables cargadas")

server = os.getenv('LDAP_SERVER')
port = int(os.getenv('LDAP_PORT', 636))

print(f"\n2. Verificando conectividad de red...")
print(f"   Servidor: {server}")
print(f"   Puerto: {port}")

# Verificar conectividad TCP
try:
    print(f"   Intentando conectar a {server}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((server, port))
    sock.close()

    if result == 0:
        print(f"   ✓ Puerto {port} está abierto")
    else:
        print(f"   ✗ Puerto {port} está cerrado o inalcanzable")
        print(f"   Código de error: {result}")
        sys.exit(1)
except socket.timeout:
    print(f"   ✗ Timeout al conectar a {server}:{port}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Error de red: {e}")
    sys.exit(1)

print("\n3. Importando módulo LDAP...")
try:
    from ldap3 import Server, Connection, Tls, SIMPLE, ALL
    import ssl
    print("   ✓ ldap3 importado")
except ImportError as e:
    print(f"   ✗ Error al importar: {e}")
    sys.exit(1)

print("\n4. Configurando conexión LDAP...")
bind_dn = os.getenv('LDAP_BIND_DN')
bind_password = os.getenv('LDAP_BIND_PASSWORD')
use_ssl = os.getenv('LDAP_USE_SSL', 'false').lower() == 'true'

print(f"   SSL: {use_ssl}")
print(f"   Bind DN: {bind_dn}")

try:
    tls_config = None
    if use_ssl:
        print("   Configurando TLS (sin validar certificado)...")
        tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)

    print("\n5. Creando servidor LDAP...")
    ldap_server = Server(
        server,
        port=port,
        use_ssl=use_ssl,
        tls=tls_config,
        get_info=ALL,
        connect_timeout=5
    )
    print("   ✓ Servidor creado")

    print("\n6. Intentando autenticación...")
    conn = Connection(
        ldap_server,
        user=bind_dn,
        password=bind_password,
        authentication=SIMPLE,
        auto_bind=True,
        receive_timeout=5
    )

    print("\n✓ ¡CONEXIÓN EXITOSA!")
    print(f"  Estado: {conn.bound}")
    print(f"  Usuario: {conn.extend.standard.who_am_i()}")

    if ldap_server.info:
        print(f"\n  Información del servidor:")
        info = ldap_server.info
        if hasattr(info, 'other'):
            for key, value in info.other.items():
                print(f"    {key}: {value}")

    conn.unbind()
    print("\n✓ Prueba completada exitosamente")

except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}")
    print(f"  Mensaje: {str(e)}")
    import traceback
    print("\nStack trace:")
    traceback.print_exc()
    sys.exit(1)
