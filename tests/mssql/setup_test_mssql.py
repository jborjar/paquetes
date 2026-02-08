"""
Script para crear la base de datos de pruebas test_python.
"""
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mssql import (
    database_exists,
    create_database,
    drop_database,
    create_table,
    table_exists
)


def setup_test_python_database():
    """Crea y configura la base de datos test_python para pruebas."""
    print("=" * 80)
    print("CONFIGURACIÓN DE BASE DE DATOS DE PRUEBAS: test_python")
    print("=" * 80)

    db_name = 'test_python'

    try:
        # 1. Verificar si existe
        print(f"\n1. Verificando si existe la base de datos '{db_name}'...")
        if database_exists(db_name):
            print(f"   La base de datos '{db_name}' ya existe.")
            response = input("   ¿Desea recrearla? (s/n): ")
            if response.lower() == 's':
                print(f"   Eliminando base de datos '{db_name}'...")
                drop_database(db_name, force=True)
                print("   ✓ Base de datos eliminada")
            else:
                print("   Manteniendo base de datos existente")
                return True

        # 2. Crear base de datos
        print(f"\n2. Creando base de datos '{db_name}'...")
        create_database(db_name)
        print("   ✓ Base de datos creada exitosamente")

        # 3. Crear tablas de ejemplo
        print("\n3. Creando tablas de ejemplo...")

        # Tabla: test_clientes
        if not table_exists('test_clientes', database=db_name):
            print("   Creando tabla 'test_clientes'...")
            create_table(
                'test_clientes',
                {
                    'id': 'INT IDENTITY(1,1)',
                    'nombre': 'NVARCHAR(100) NOT NULL',
                    'email': 'NVARCHAR(100)',
                    'telefono': 'NVARCHAR(20)',
                    'activo': 'BIT DEFAULT 1',
                    'fecha_registro': 'DATETIME DEFAULT GETDATE()'
                },
                primary_key='id',
                database=db_name
            )
            print("   ✓ Tabla 'test_clientes' creada")

        # Tabla: test_productos
        if not table_exists('test_productos', database=db_name):
            print("   Creando tabla 'test_productos'...")
            create_table(
                'test_productos',
                {
                    'id': 'INT IDENTITY(1,1)',
                    'codigo': 'NVARCHAR(50) NOT NULL',
                    'nombre': 'NVARCHAR(100)',
                    'descripcion': 'NVARCHAR(MAX)',
                    'precio': 'DECIMAL(18,2)',
                    'stock': 'INT DEFAULT 0',
                    'activo': 'BIT DEFAULT 1',
                    'fecha_creacion': 'DATETIME DEFAULT GETDATE()'
                },
                primary_key='id',
                database=db_name
            )
            print("   ✓ Tabla 'test_productos' creada")

        # Tabla: test_ventas
        if not table_exists('test_ventas', database=db_name):
            print("   Creando tabla 'test_ventas'...")
            create_table(
                'test_ventas',
                {
                    'id': 'INT IDENTITY(1,1)',
                    'cliente_id': 'INT',
                    'producto_id': 'INT',
                    'cantidad': 'INT NOT NULL',
                    'precio_unitario': 'DECIMAL(18,2)',
                    'total': 'DECIMAL(18,2)',
                    'fecha_venta': 'DATETIME DEFAULT GETDATE()'
                },
                primary_key='id',
                database=db_name
            )
            print("   ✓ Tabla 'test_ventas' creada")

        print("\n" + "=" * 80)
        print(f"✓ BASE DE DATOS '{db_name}' CONFIGURADA EXITOSAMENTE")
        print("=" * 80)
        print("\nTablas creadas:")
        print("  - test_clientes   (para pruebas de clientes)")
        print("  - test_productos  (para pruebas de productos)")
        print("  - test_ventas     (para pruebas de ventas)")
        print("\nPuedes ejecutar los tests con:")
        print("  docker exec api-mcp python /app/mssql/run_all_tests.py")
        print("=" * 80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Error configurando la base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_database_info():
    """Muestra información de la base de datos test_python."""
    db_name = 'test_python'

    print("\n" + "=" * 80)
    print(f"INFORMACIÓN DE LA BASE DE DATOS: {db_name}")
    print("=" * 80)

    try:
        if not database_exists(db_name):
            print(f"\n❌ La base de datos '{db_name}' no existe.")
            print("   Ejecuta este script para crearla.")
            return

        from mssql import execute_query, get_table_columns

        # Listar tablas
        tables = execute_query("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """, database=db_name)

        print(f"\nTablas en '{db_name}':")
        for table in tables:
            print(f"  - {table[0]}")

            # Mostrar columnas de cada tabla
            columns = get_table_columns(table[0], database=db_name)
            print(f"    Columnas ({len(columns)}):")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] else "NOT NULL"
                print(f"      • {col['name']}: {col['type']} {nullable}")
            print()

        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Error obteniendo información: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'info':
        # Modo información
        show_database_info()
    else:
        # Modo setup
        if setup_test_python_database():
            # Mostrar información después de crear
            show_database_info()
            sys.exit(0)
        else:
            sys.exit(1)
