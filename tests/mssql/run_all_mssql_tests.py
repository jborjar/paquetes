"""
Script de pruebas automáticas para el módulo MSSQL.
Ejecuta TODOS los tests sin interacción del usuario.
"""
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_mssql import (
    setup_test_environment,
    test_dml,
    test_ddl,
    test_connections,
    test_dcl
)


def main():
    """Ejecuta todos los tests automáticamente."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║               MÓDULO MSSQL - SUITE COMPLETA DE PRUEBAS                    ║
╚═══════════════════════════════════════════════════════════════════════════╝

Ejecutando TODOS los tests automáticamente:
- DML (Data Manipulation Language)
- DDL (Data Definition Language)
- Gestión de Conexiones
- DCL (Data Control Language)

Base de datos: test
Servidor: mssql-api-mcp
    """)

    # Setup
    print("Configurando ambiente de pruebas...")
    if not setup_test_environment():
        print("\n❌ No se pudo configurar el ambiente de pruebas")
        sys.exit(1)

    # Ejecutar todos los tests
    all_passed = True
    total_tests = 0
    passed_tests = 0

    tests = [
        ("DML", test_dml),
        ("DDL", test_ddl),
        ("Gestión de Conexiones", test_connections),
        ("DCL", test_dcl)
    ]

    for test_name, test_func in tests:
        try:
            print(f"\n{'='*80}")
            print(f"Ejecutando tests de {test_name}...")
            print(f"{'='*80}")

            result = test_func()
            if result:
                passed_tests += 1
            else:
                all_passed = False
            total_tests += 1

        except Exception as e:
            print(f"\n❌ Error ejecutando tests de {test_name}: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
            total_tests += 1

    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"\nCategorías de tests ejecutadas: {passed_tests}/{total_tests}")

    if all_passed:
        print("\n✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("\nEstadísticas:")
        print("  - DML: 10 tests ✓")
        print("  - DDL: 9 tests ✓")
        print("  - Gestión de Conexiones: 5 tests ✓")
        print("  - DCL: Variable (depende de permisos) ✓")
    else:
        print("\n❌ ALGUNAS CATEGORÍAS DE PRUEBAS FALLARON")
        print(f"   Revisa los logs arriba para más detalles")

    print("=" * 80 + "\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
