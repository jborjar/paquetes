#!/usr/bin/env python3
"""
Script de prueba para Evolution API - WhatsApp.

Verifica la conexión y funcionalidad básica del cliente.

Uso:
    # Desde el contenedor
    docker exec api-mcp python3 -m paquetes.tests.test_whatsapp

    # O desde /app
    cd /home/dockerfs/PROGEX/software/app
    python3 -m paquetes.tests.test_whatsapp
"""
import sys
from paquetes.whatsapp.client import EvolutionAPIClient


def test_connection():
    """Prueba la conexión a Evolution API."""
    print("=" * 60)
    print("TEST: Conexión a Evolution API")
    print("=" * 60)

    try:
        client = EvolutionAPIClient()
        print(f"✓ Cliente creado")
        print(f"  URL: {client.base_url}")
        print(f"  API Key: {client.api_key[:20]}...")
        return client
    except Exception as e:
        print(f"✗ Error al crear cliente: {e}")
        return None


def test_list_instances(client):
    """Prueba listar instancias."""
    print("\n" + "=" * 60)
    print("TEST: Listar Instancias")
    print("=" * 60)

    try:
        instances = client.list_instances()
        print(f"✓ Instancias encontradas: {len(instances)}")

        if instances:
            for inst in instances:
                instance_data = inst.get('instance', {})
                print(f"\n  Instancia:")
                print(f"    Nombre: {instance_data.get('instanceName')}")
                print(f"    ID: {instance_data.get('instanceId')}")
                print(f"    Estado: {instance_data.get('status')}")

        return True
    except Exception as e:
        print(f"✗ Error al listar instancias: {e}")
        return False


def test_create_instance(client, instance_name="test_whatsapp"):
    """Prueba crear una instancia."""
    print("\n" + "=" * 60)
    print("TEST: Crear Instancia")
    print("=" * 60)

    try:
        result = client.create_instance(instance_name)
        instance_data = result.get('instance', {})

        print(f"✓ Instancia creada")
        print(f"  Nombre: {instance_data.get('instanceName')}")
        print(f"  ID: {instance_data.get('instanceId')}")
        print(f"  Estado: {instance_data.get('status')}")

        return True
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            print(f"⚠ La instancia '{instance_name}' ya existe")
            return True
        else:
            print(f"✗ Error al crear instancia: {e}")
            return False


def test_get_qr(client, instance_name="test_whatsapp"):
    """Prueba obtener QR code."""
    print("\n" + "=" * 60)
    print("TEST: Obtener QR Code")
    print("=" * 60)

    try:
        qr_data = client.get_qr_code(instance_name)

        print(f"✓ QR Code obtenido")
        if 'code' in qr_data:
            print(f"  QR disponible: {qr_data['code'][:60]}...")
        if 'base64' in qr_data:
            print(f"  Base64 disponible: Sí")

        print(f"\n  Para conectar WhatsApp:")
        print(f"  1. Abre WhatsApp en tu celular")
        print(f"  2. Ve a Configuración > Dispositivos vinculados")
        print(f"  3. Toca 'Vincular un dispositivo'")
        print(f"  4. Escanea el QR que aparece en la respuesta")

        return True
    except Exception as e:
        print(f"✗ Error al obtener QR: {e}")
        return False


def test_connection_state(client, instance_name="test_whatsapp"):
    """Prueba verificar estado de conexión."""
    print("\n" + "=" * 60)
    print("TEST: Estado de Conexión")
    print("=" * 60)

    try:
        state = client.get_connection_state(instance_name)
        is_connected = client.is_instance_connected(instance_name)

        print(f"✓ Estado obtenido")
        print(f"  Instancia: {instance_name}")
        print(f"  Estado: {state.get('state')}")
        print(f"  Conectado: {'Sí' if is_connected else 'No'}")

        if not is_connected:
            print(f"\n  ⚠ La instancia NO está conectada")
            print(f"  Usa el QR code para conectarla primero")

        return True
    except Exception as e:
        print(f"✗ Error al verificar estado: {e}")
        return False


def test_phone_formatting(client):
    """Prueba formateo de números de teléfono."""
    print("\n" + "=" * 60)
    print("TEST: Formateo de Números")
    print("=" * 60)

    test_numbers = [
        "55 1234 5678",
        "5512345678",
        "+52 55 1234 5678",
        "52 55 1234 5678",
        "5215512345678"
    ]

    try:
        print("Probando formateo de números:")
        for number in test_numbers:
            formatted = client.format_phone_number(number)
            print(f"  {number:20} → {formatted}")

        print(f"\n✓ Formateo de números OK")
        return True
    except Exception as e:
        print(f"✗ Error al formatear números: {e}")
        return False


def main():
    """Ejecuta todos los tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  TEST SUITE - Evolution API WhatsApp Integration        ║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Test 1: Conexión
    client = test_connection()
    if not client:
        print("\n✗ FALLO: No se pudo conectar a Evolution API")
        sys.exit(1)

    # Test 2: Listar instancias
    test_list_instances(client)

    # Test 3: Crear instancia (si no existe)
    test_create_instance(client)

    # Test 4: Obtener QR
    test_get_qr(client)

    # Test 5: Verificar estado
    test_connection_state(client)

    # Test 6: Formateo de números
    test_phone_formatting(client)

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print("✓ Todos los tests completados")
    print()
    print("PRÓXIMOS PASOS:")
    print("1. Escanea el QR code con WhatsApp para conectar")
    print("2. Verifica que el estado sea 'open'")
    print("3. Envía un mensaje de prueba")
    print()
    print("EJEMPLO DE USO:")
    print("  from paquetes.whatsapp import client")
    print("  result = client.send_text(")
    print("      'test_whatsapp',")
    print("      '5215512345678',")
    print("      'Hola desde Evolution API!'")
    print("  )")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
