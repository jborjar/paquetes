#!/usr/bin/env python3
"""
Test del módulo csf_validator.

Este script demuestra el uso del validador genérico de CSF.
"""
import sys
import os

# Usar el módulo genérico
from paquetes.sat.csf_validator import validate_csf_full

# RFC para prueba
RFC_PRUEBA = "BORJ720323KD9"

print("=" * 70)
print("TEST: Validador CSF (Módulo Genérico)")
print("=" * 70)
print(f"RFC: {RFC_PRUEBA}")
print()

# Nota: Para probar con un PDF real, proporciona la ruta
print("NOTA: Este test requiere un archivo PDF de CSF.")
print("      Para probar, ejecuta:")
print()
print(f"      python -m paquetes.tests.sat.test_csf_validator <archivo.pdf>")
print()

if len(sys.argv) > 1:
    pdf_file = sys.argv[1]

    print(f"Validando: {pdf_file}")
    print()

    # Validación completa con reporte HTML
    result = validate_csf_full(
        pdf_file=pdf_file,
        expected_rfc=RFC_PRUEBA if len(sys.argv) == 2 else sys.argv[2]
    )

    if result['success']:
        data = result['validation_data']

        print("✓ VALIDACIÓN EXITOSA")
        print()
        print("Datos obtenidos:")
        print(f"  RFC: {data['rfc']}")
        print(f"  Tipo: {data.get('tipo_persona', 'N/A')}")
        print(f"  Estado: {data.get('estado', 'Desconocido')}")
        print(f"  Activo: {'Sí' if data.get('activo') else 'No'}")
        print(f"  Seguro para transaccionar: {'Sí' if data.get('seguro_transaccionar') else 'No'}")

        if data.get('regimenes'):
            print(f"\n  Regímenes:")
            for reg in data['regimenes']:
                print(f"    - {reg}")

        if data.get('riesgos'):
            print(f"\n  ⚠️  Riesgos detectados:")
            for riesgo in data['riesgos']:
                print(f"    - {riesgo}")

        if result.get('html_file'):
            print(f"\n  Reporte HTML: {result['html_file']}")

        print()
        print("=" * 70)
    else:
        print(f"✗ ERROR: {result.get('error')}")
        sys.exit(1)
else:
    print("Uso del módulo genérico:")
    print()
    print("  from paquetes.sat.csf_validator import validate_csf_full")
    print()
    print("  # Validación completa con reporte HTML")
    print("  result = validate_csf_full(")
    print("      pdf_file='constancia.pdf',")
    print("      expected_rfc='XAXX010101000',")
    print("      output_html='reporte.html'")
    print("  )")
    print()
    print("  if result['success']:")
    print("      data = result['validation_data']")
    print("      print(f\"RFC: {data['rfc']}\")")
    print("      print(f\"Estado: {data['estado']}\")")
    print("      print(f\"Seguro: {data['seguro_transaccionar']}\")")
    print("      print(f\"Reporte: {result['html_file']}\")")
    print()
    print("=" * 70)
