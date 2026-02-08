"""
Ejemplo de uso del módulo SAT - Facturación Electrónica CFDI.

Este script demuestra las principales funcionalidades del paquete sat:
- Generación de CFDI
- Validación de estructura
- Timbrado con PAC
- Validación de RFC
- Descarga masiva del SAT

Configuración requerida en .env:
    SAT_EMISOR_RFC
    SAT_EMISOR_NOMBRE
    SAT_PAC_PROVIDER
    SAT_PAC_USERNAME
    SAT_PAC_PASSWORD
    SAT_FIEL_CER (para descarga masiva)
    SAT_FIEL_KEY
    SAT_FIEL_PASSWORD
"""
import os
import sys

# Agregar path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sat import (
    # Generación
    create_cfdi_ingreso,
    create_cfdi_egreso,
    # Validación
    validate_cfdi_structure,
    validate_rfc_format,
    extract_cfdi_data,
    # Timbrado
    stamp_cfdi,
    # RFC
    is_rfc_safe_to_transact,
    check_rfc_status_in_sat,
    # Descarga
    download_cfdi_full_process
)


def demo_generar_cfdi():
    """Demo de generación de CFDI."""
    print("\n" + "=" * 60)
    print("DEMO: Generar CFDI de Ingreso (Factura)")
    print("=" * 60)

    emisor = {
        'rfc': os.getenv('SAT_EMISOR_RFC', 'XAXX010101000'),
        'nombre': os.getenv('SAT_EMISOR_NOMBRE', 'MI EMPRESA SA DE CV'),
        'regimen_fiscal': '601'
    }

    receptor = {
        'rfc': 'XEXX010101000',
        'nombre': 'CLIENTE EJEMPLO SA DE CV',
        'uso_cfdi': 'G03',
        'domicilio_fiscal_receptor': '12345',
        'regimen_fiscal_receptor': '612'
    }

    conceptos = [{
        'clave_prod_serv': '01010101',
        'cantidad': 1,
        'clave_unidad': 'E48',
        'unidad': 'Servicio',
        'descripcion': 'Servicio de consultoría tecnológica',
        'valor_unitario': 1000.00,
        'importe': 1000.00,
        'objeto_imp': '02',
        'impuestos': {
            'traslados': [{
                'base': 1000.00,
                'impuesto': '002',
                'tipo_factor': 'Tasa',
                'tasa_o_cuota': 0.16,
                'importe': 160.00
            }]
        }
    }]

    print("\n1. Generando CFDI...")
    result = create_cfdi_ingreso(
        emisor=emisor,
        receptor=receptor,
        conceptos=conceptos,
        forma_pago='03',  # Transferencia
        metodo_pago='PUE',  # Pago en una exhibición
        lugar_expedicion='12345'
    )

    if result['success']:
        print("✓ CFDI generado exitosamente")
        print(f"  Tipo: {result['tipo_comprobante']}")
        print(f"  Versión: {result['version']}")
        print(f"  Total: ${result['total']:.2f}")
        return result['xml']
    else:
        print(f"✗ Error: {result['error']}")
        return None


def demo_validar_cfdi(xml_cfdi):
    """Demo de validación de CFDI."""
    print("\n" + "=" * 60)
    print("DEMO: Validar Estructura de CFDI")
    print("=" * 60)

    if not xml_cfdi:
        print("✗ No hay CFDI para validar")
        return

    print("\n1. Validando estructura XML...")
    result = validate_cfdi_structure(xml_cfdi)

    if result['valid']:
        print("✓ Estructura válida")
        print(f"  Versión CFDI: {result['version']}")
        if result['warnings']:
            print(f"  Advertencias: {len(result['warnings'])}")
            for warning in result['warnings']:
                print(f"    - {warning}")
    else:
        print("✗ Estructura inválida")
        print(f"  Errores encontrados: {len(result['errors'])}")
        for error in result['errors']:
            print(f"    - {error}")

    print("\n2. Extrayendo datos del CFDI...")
    try:
        datos = extract_cfdi_data(xml_cfdi)
        print("✓ Datos extraídos:")
        print(f"  Emisor: {datos.get('emisor', {}).get('nombre')}")
        print(f"  Receptor: {datos.get('receptor', {}).get('nombre')}")
        print(f"  Total: ${datos.get('total', 0):.2f}")
        print(f"  Conceptos: {len(datos.get('conceptos', []))}")
    except Exception as e:
        print(f"✗ Error al extraer datos: {str(e)}")


def demo_timbrar_cfdi(xml_cfdi):
    """Demo de timbrado con PAC."""
    print("\n" + "=" * 60)
    print("DEMO: Timbrar CFDI con PAC")
    print("=" * 60)

    if not xml_cfdi:
        print("✗ No hay CFDI para timbrar")
        return

    pac_provider = os.getenv('SAT_PAC_PROVIDER')
    pac_username = os.getenv('SAT_PAC_USERNAME')
    pac_password = os.getenv('SAT_PAC_PASSWORD')

    if not all([pac_provider, pac_username, pac_password]):
        print("⚠️  Credenciales del PAC no configuradas en .env")
        print("   Saltando demo de timbrado")
        return

    print(f"\n1. Timbrando con PAC: {pac_provider}...")
    result = stamp_cfdi(
        xml_string=xml_cfdi,
        pac_provider=pac_provider,
        username=pac_username,
        password=pac_password
    )

    if result['success']:
        print("✓ CFDI timbrado exitosamente")
        print(f"  UUID: {result['timbre']['uuid']}")
        print(f"  Fecha timbrado: {result['timbre']['fecha_timbrado']}")
        print(f"  PAC: {result['pac']}")
    else:
        print(f"✗ Error al timbrar: {result['error']}")


def demo_validar_rfc():
    """Demo de validación de RFC."""
    print("\n" + "=" * 60)
    print("DEMO: Validación de RFC")
    print("=" * 60)

    rfcs_prueba = [
        'XAXX010101000',  # RFC genérico
        'XEXX010101000',  # RFC genérico
        'ABC123456XXX',   # RFC inválido
    ]

    for rfc in rfcs_prueba:
        print(f"\n1. Validando RFC: {rfc}")

        # Validar formato
        formato = validate_rfc_format(rfc)
        if formato['valid']:
            print(f"   ✓ Formato válido: {formato['tipo']}")
        else:
            print(f"   ✗ Formato inválido: {formato['error']}")
            continue

        # Verificar si es seguro transaccionar
        print("   2. Verificando en listas del SAT...")
        seguridad = is_rfc_safe_to_transact(rfc)

        if seguridad['seguro']:
            print(f"   ✓ RFC aprobado para transacciones")
        else:
            print(f"   ⚠️  RFC con riesgos:")
            for riesgo in seguridad['riesgos']:
                print(f"      - {riesgo}")


def demo_consultar_sat():
    """Demo de consulta de situación fiscal."""
    print("\n" + "=" * 60)
    print("DEMO: Consulta de Situación en el SAT")
    print("=" * 60)

    rfc = os.getenv('SAT_EMISOR_RFC', 'XAXX010101000')

    print(f"\n1. Consultando RFC: {rfc}")
    result = check_rfc_status_in_sat(rfc)

    if result['success']:
        print("✓ Información obtenida:")
        print(f"  Nombre: {result['nombre']}")
        print(f"  Tipo: {result['tipo_persona']}")
        print(f"  Estado: {result['situacion_fiscal']}")
        print(f"  Activo: {'Sí' if result['activo'] else 'No'}")

        if result['regimen_fiscal']:
            print(f"  Regímenes fiscales:")
            for regimen in result['regimen_fiscal']:
                print(f"    - {regimen}")
    else:
        print(f"✗ Error: {result['error']}")


def demo_descarga_masiva():
    """Demo de descarga masiva del SAT."""
    print("\n" + "=" * 60)
    print("DEMO: Descarga Masiva de CFDIs")
    print("=" * 60)

    fiel_cer = os.getenv('SAT_FIEL_CER')
    fiel_key = os.getenv('SAT_FIEL_KEY')
    fiel_password = os.getenv('SAT_FIEL_PASSWORD')

    if not all([fiel_cer, fiel_key, fiel_password]):
        print("⚠️  Credenciales de FIEL no configuradas en .env")
        print("   Saltando demo de descarga masiva")
        return

    rfc = os.getenv('SAT_EMISOR_RFC', 'XAXX010101000')

    print(f"\n1. Solicitando descarga para RFC: {rfc}")
    print("   Período: Enero 2026")
    print("   Tipo: CFDIs emitidos")

    result = download_cfdi_full_process(
        rfc=rfc,
        fecha_inicio='2026-01-01',
        fecha_fin='2026-01-31',
        tipo='emitidos',
        output_dir='./descargas_sat_demo',
        wait_timeout=60,  # 1 minuto
        certificado=fiel_cer,
        key_file=fiel_key,
        key_password=fiel_password
    )

    if result['success']:
        print("✓ Descarga completada")
        print(f"  CFDIs descargados: {result['total_cfdis']}")
        print(f"  Directorio: {result['directorio']}")
        print(f"  Solicitud ID: {result['solicitud_id']}")
    else:
        print(f"✗ Error: {result['error']}")


def main():
    """Función principal."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "EJEMPLO - MÓDULO SAT (CFDI)" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Verificar dependencias
    try:
        import satcfdi
        print("✓ Librería satcfdi instalada")
    except ImportError:
        print("⚠️  Librería satcfdi no instalada")
        print("   Ejecutar: pip install satcfdi")
        print()

    # Menú de opciones
    while True:
        print("\n" + "-" * 60)
        print("OPCIONES:")
        print("  1. Generar CFDI")
        print("  2. Validar estructura de CFDI")
        print("  3. Timbrar CFDI con PAC")
        print("  4. Validar RFCs")
        print("  5. Consultar situación en el SAT")
        print("  6. Descarga masiva de CFDIs")
        print("  7. Flujo completo (generar + validar + timbrar)")
        print("  0. Salir")
        print("-" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == '1':
            xml_cfdi = demo_generar_cfdi()
        elif opcion == '2':
            xml_cfdi = demo_generar_cfdi()
            if xml_cfdi:
                demo_validar_cfdi(xml_cfdi)
        elif opcion == '3':
            xml_cfdi = demo_generar_cfdi()
            if xml_cfdi:
                demo_timbrar_cfdi(xml_cfdi)
        elif opcion == '4':
            demo_validar_rfc()
        elif opcion == '5':
            demo_consultar_sat()
        elif opcion == '6':
            demo_descarga_masiva()
        elif opcion == '7':
            # Flujo completo
            xml_cfdi = demo_generar_cfdi()
            if xml_cfdi:
                demo_validar_cfdi(xml_cfdi)
                demo_timbrar_cfdi(xml_cfdi)
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
