"""
Script de pruebas para el módulo PostgreSQL.

Este script prueba las funcionalidades básicas del módulo postgres.
"""
from paquetes.postgres import (
    get_postgres_connection,
    ping, database_exists, table_exists,
    create_table, insert, select, update, delete
)


def test_conexion():
    """Prueba la conexión a PostgreSQL."""
    print("\n=== TEST: Conexión a PostgreSQL ===")
    try:
        conn = get_postgres_connection()
        print("✓ Conexión exitosa")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False


def test_operaciones_basicas():
    """Prueba operaciones básicas DML."""
    print("\n=== TEST: Operaciones Básicas ===")

    try:
        # Crear tabla de prueba
        print("Creando tabla de prueba...")
        create_table(
            'test_empresas',
            {
                'id': 'SERIAL',
                'codigo': 'VARCHAR(50) UNIQUE NOT NULL',
                'nombre': 'VARCHAR(200) NOT NULL',
                'activo': 'BOOLEAN DEFAULT TRUE'
            },
            primary_key='id',
            if_not_exists=True
        )
        print("✓ Tabla creada")

        # Insertar
        print("Insertando registro...")
        insert('test_empresas', {
            'codigo': 'TEST001',
            'nombre': 'Empresa de Prueba',
            'activo': True
        })
        print("✓ Registro insertado")

        # Seleccionar
        print("Consultando registros...")
        empresas = select('test_empresas')
        print(f"✓ Encontradas {len(empresas)} empresas")

        # Actualizar
        print("Actualizando registro...")
        update(
            'test_empresas',
            {'nombre': 'Empresa Actualizada'},
            where='codigo = %s',
            where_params=('TEST001',)
        )
        print("✓ Registro actualizado")

        # Eliminar
        print("Eliminando registro...")
        delete('test_empresas', where='codigo = %s', where_params=('TEST001',))
        print("✓ Registro eliminado")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("=" * 60)
    print("PRUEBAS DEL MÓDULO POSTGRESQL")
    print("=" * 60)

    resultados = []

    # Prueba de conexión
    resultados.append(('Conexión', test_conexion()))

    # Pruebas de operaciones básicas
    resultados.append(('Operaciones Básicas', test_operaciones_basicas()))

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)

    exitosas = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nombre, resultado in resultados:
        estado = "✓ PASÓ" if resultado else "✗ FALLÓ"
        print(f"{estado} - {nombre}")

    print(f"\nTotal: {exitosas}/{total} pruebas exitosas")

    if exitosas == total:
        print("\n✓ TODAS LAS PRUEBAS PASARON")
    else:
        print("\n✗ ALGUNAS PRUEBAS FALLARON")


if __name__ == '__main__':
    main()
