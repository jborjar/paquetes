"""
Script de pruebas para el módulo SAP HANA.
Ejecuta tests de DML, DDL y DCL usando el schema 'TEST_PYTHON'.

⚠️ ADVERTENCIA: Solo ejecutar en ambiente de desarrollo.
"""
import sys
import os
import traceback
from typing import Callable

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name: str):
        self.passed += 1
        print(f"  ✓ {test_name}")

    def record_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ✗ {test_name}: {error}")

    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 80)
        print(f"RESUMEN: {self.passed}/{total} pruebas exitosas")
        if self.errors:
            print(f"\n❌ {self.failed} pruebas fallidas:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        else:
            print("\n✓ Todas las pruebas pasaron exitosamente")
        print("=" * 80)


def run_test(func: Callable, test_name: str, result: TestResult):
    """Ejecuta una prueba y registra el resultado."""
    try:
        func()
        result.record_pass(test_name)
        return True
    except Exception as e:
        result.record_fail(test_name, str(e))
        return False


# ============================================================================
# TESTS DML
# ============================================================================

def test_dml():
    """Tests de Data Manipulation Language."""
    print("\n" + "=" * 80)
    print("TESTS DML - DATA MANIPULATION LANGUAGE (SAP HANA)")
    print("=" * 80)

    from hana import (
        insert, insert_many, select, select_one,
        update, delete, exists, count, upsert
    )

    result = TestResult()
    test_schema = 'TEST_PYTHON'

    # Test INSERT
    def test_insert():
        insert('TEST_CLIENTES', {
            'NOMBRE': 'Test Cliente 1',
            'EMAIL': 'test1@email.com',
            'TELEFONO': '5551111111'
        }, schema=test_schema)

    run_test(test_insert, "INSERT - Insertar registro", result)

    # Test INSERT_MANY
    def test_insert_many():
        datos = [
            ('Test Cliente 2', 'test2@email.com', '5552222222'),
            ('Test Cliente 3', 'test3@email.com', '5553333333'),
            ('Test Cliente 4', 'test4@email.com', '5554444444')
        ]
        total = insert_many(
            'TEST_CLIENTES',
            ['NOMBRE', 'EMAIL', 'TELEFONO'],
            datos,
            schema=test_schema
        )
        assert total >= 3, f"Debe insertar al menos 3 registros, insertó {total}"

    run_test(test_insert_many, "INSERT_MANY - Inserción masiva", result)

    # Test SELECT
    def test_select():
        registros = select('TEST_CLIENTES', schema=test_schema)
        assert len(registros) >= 4, f"Se esperaban al menos 4 registros, se obtuvieron {len(registros)}"

    run_test(test_select, "SELECT - Consultar registros", result)

    # Test SELECT con filtros
    def test_select_filtered():
        registros = select(
            'TEST_CLIENTES',
            where='"ACTIVO" = ?',
            where_params=(1,),
            schema=test_schema
        )
        assert len(registros) >= 1, "Debe haber al menos 1 registro activo"

    run_test(test_select_filtered, "SELECT - Con filtros", result)

    # Test SELECT_ONE
    def test_select_one():
        registro = select_one(
            'TEST_CLIENTES',
            where='"NOMBRE" = ?',
            where_params=('Test Cliente 1',),
            schema=test_schema
        )
        assert registro is not None, "Debe encontrar el registro"
        assert registro[1] == 'Test Cliente 1', "El nombre debe coincidir"

    run_test(test_select_one, "SELECT_ONE - Consultar un registro", result)

    # Test EXISTS
    def test_exists():
        existe = exists(
            'TEST_CLIENTES',
            where='"EMAIL" = ?',
            where_params=('test1@email.com',),
            schema=test_schema
        )
        assert existe, "El registro debe existir"

    run_test(test_exists, "EXISTS - Verificar existencia", result)

    # Test COUNT
    def test_count():
        total = count('TEST_CLIENTES', schema=test_schema)
        assert total >= 4, f"Debe haber al menos 4 registros, hay {total}"

    run_test(test_count, "COUNT - Contar registros", result)

    # Test UPDATE
    def test_update():
        rows = update(
            'TEST_CLIENTES',
            data={'TELEFONO': '5559999999'},
            where='"NOMBRE" = ?',
            where_params=('Test Cliente 1',),
            schema=test_schema
        )
        assert rows >= 1, f"Debe actualizar al menos 1 registro, actualizó {rows}"

    run_test(test_update, "UPDATE - Actualizar registros", result)

    # Test UPSERT
    def test_upsert():
        # Insertar primero
        insert('TEST_CLIENTES', {
            'NOMBRE': 'Test Upsert',
            'EMAIL': 'upsert@test.com',
            'TELEFONO': '5558888888'
        }, schema=test_schema)

        # Actualizar con upsert
        rowcount, operation = upsert(
            'TEST_CLIENTES',
            data={
                'NOMBRE': 'Test Upsert',
                'EMAIL': 'upsert_updated@test.com',
                'TELEFONO': '5559999999'
            },
            key_columns=['NOMBRE'],
            schema=test_schema
        )
        assert operation == 'updated', f"Debe ser UPDATE, fue {operation}"

    run_test(test_upsert, "UPSERT - Update por key", result)

    # Test DELETE
    def test_delete():
        rows = delete(
            'TEST_CLIENTES',
            where='"EMAIL" = ?',
            where_params=('upsert_updated@test.com',),
            schema=test_schema
        )
        assert rows >= 1, f"Debe eliminar al menos 1 registro, eliminó {rows}"

    run_test(test_delete, "DELETE - Eliminar registros", result)

    result.summary()
    return result.failed == 0


# ============================================================================
# TESTS DDL
# ============================================================================

def test_ddl():
    """Tests de Data Definition Language."""
    print("\n" + "=" * 80)
    print("TESTS DDL - DATA DEFINITION LANGUAGE (SAP HANA)")
    print("=" * 80)

    from hana import (
        schema_exists, table_exists, create_table, drop_table,
        create_index, drop_index, execute_ddl, get_table_columns,
        truncate_table
    )

    result = TestResult()
    test_schema = 'TEST_PYTHON'

    # Test SCHEMA_EXISTS
    def test_schema_exists():
        existe = schema_exists(test_schema)
        assert existe, f"El schema '{test_schema}' debe existir"

    run_test(test_schema_exists, "SCHEMA_EXISTS - Verificar schema", result)

    # Test TABLE_EXISTS
    def test_table_exists():
        existe = table_exists('TEST_CLIENTES', schema=test_schema)
        assert existe, "La tabla 'TEST_CLIENTES' debe existir"

    run_test(test_table_exists, "TABLE_EXISTS - Verificar tabla", result)

    # Test CREATE_TABLE
    def test_create_table():
        created = create_table(
            'TEST_TEMP',
            {
                'ID': 'INTEGER GENERATED BY DEFAULT AS IDENTITY',
                'CODIGO': 'NVARCHAR(50) NOT NULL',
                'NOMBRE': 'NVARCHAR(100)',
                'VALOR': 'DECIMAL(18,2)'
            },
            primary_key='ID',
            table_type='COLUMN',
            schema=test_schema
        )
        assert created, "La tabla debe crearse exitosamente"

    run_test(test_create_table, "CREATE_TABLE - Crear tabla COLUMN", result)

    # Test GET_TABLE_COLUMNS
    def test_get_table_columns():
        columnas = get_table_columns('TEST_TEMP', schema=test_schema)
        assert len(columnas) >= 4, f"Debe haber al menos 4 columnas, hay {len(columnas)}"
        nombres = [c['name'].upper() for c in columnas]
        assert 'ID' in nombres, "Debe existir columna 'ID'"

    run_test(test_get_table_columns, "GET_TABLE_COLUMNS - Estructura", result)

    # Test CREATE_INDEX
    def test_create_index():
        created = create_index(
            'TEST_TEMP',
            'IDX_CODIGO',
            'CODIGO',
            schema=test_schema
        )
        assert created, "El índice debe crearse exitosamente"

    run_test(test_create_index, "CREATE_INDEX - Crear índice", result)

    # Test TRUNCATE_TABLE
    def test_truncate():
        # Insertar datos primero
        from hana import insert
        insert('TEST_TEMP', {
            'CODIGO': 'T001',
            'NOMBRE': 'Temp 1',
            'VALOR': 100.00
        }, schema=test_schema)

        # Truncar
        truncate_table('TEST_TEMP', schema=test_schema)

        # Verificar
        from hana import count
        total = count('TEST_TEMP', schema=test_schema)
        assert total == 0, f"La tabla debe estar vacía, tiene {total} registros"

    run_test(test_truncate, "TRUNCATE_TABLE - Vaciar tabla", result)

    # Test DROP_INDEX
    def test_drop_index():
        deleted = drop_index('IDX_CODIGO', schema=test_schema)
        assert deleted, "El índice debe eliminarse exitosamente"

    run_test(test_drop_index, "DROP_INDEX - Eliminar índice", result)

    # Test DROP_TABLE
    def test_drop_table():
        deleted = drop_table('TEST_TEMP', schema=test_schema)
        assert deleted, "La tabla debe eliminarse exitosamente"

    run_test(test_drop_table, "DROP_TABLE - Eliminar tabla", result)

    result.summary()
    return result.failed == 0


# ============================================================================
# TESTS DCL
# ============================================================================

def test_dcl():
    """Tests de Data Control Language."""
    print("\n" + "=" * 80)
    print("TESTS DCL - DATA CONTROL LANGUAGE (SAP HANA)")
    print("=" * 80)
    print("⚠️  Requiere permisos de administrador\n")

    from hana import (
        user_exists, create_user, drop_user,
        grant_permission, get_user_permissions,
        role_exists, create_role, drop_role,
        grant_role, get_user_roles
    )

    result = TestResult()
    test_schema = 'TEST_PYTHON'

    # Test CREATE_USER
    def test_create_user():
        # Eliminar si existe
        if user_exists('TEST_USER_DEMO'):
            drop_user('TEST_USER_DEMO')

        created = create_user('TEST_USER_DEMO', 'TestPass123')
        assert created, "El usuario debe crearse exitosamente"

    run_test(test_create_user, "CREATE_USER - Crear usuario", result)

    # Test USER_EXISTS
    def test_user_exists():
        existe = user_exists('TEST_USER_DEMO')
        assert existe, "El usuario 'TEST_USER_DEMO' debe existir"

    run_test(test_user_exists, "USER_EXISTS - Verificar usuario", result)

    # Test GRANT_PERMISSION
    def test_grant_permission():
        grant_permission('SELECT', user_name='TEST_USER_DEMO', schema=test_schema)

    run_test(test_grant_permission, "GRANT_PERMISSION - Otorgar permiso", result)

    # Test GET_USER_PERMISSIONS
    def test_get_user_permissions():
        permisos = get_user_permissions('TEST_USER_DEMO')
        assert len(permisos) > 0, "Debe tener al menos 1 permiso"

    run_test(test_get_user_permissions, "GET_USER_PERMISSIONS - Consultar permisos", result)

    # Test CREATE_ROLE
    def test_create_role():
        if role_exists('TEST_ROLE'):
            drop_role('TEST_ROLE')

        created = create_role('TEST_ROLE')
        assert created, "El rol debe crearse exitosamente"

    run_test(test_create_role, "CREATE_ROLE - Crear rol", result)

    # Test GRANT_ROLE
    def test_grant_role():
        grant_role('TEST_ROLE', 'TEST_USER_DEMO')

    run_test(test_grant_role, "GRANT_ROLE - Asignar rol", result)

    # Test GET_USER_ROLES
    def test_get_user_roles():
        roles = get_user_roles('TEST_USER_DEMO')
        assert 'TEST_ROLE' in roles, "Debe tener el rol 'TEST_ROLE'"

    run_test(test_get_user_roles, "GET_USER_ROLES - Consultar roles", result)

    # Cleanup
    def test_cleanup():
        drop_user('TEST_USER_DEMO')
        drop_role('TEST_ROLE')

    run_test(test_cleanup, "CLEANUP - Limpiar usuarios y roles", result)

    result.summary()
    return result.failed == 0


# ============================================================================
# TESTS GESTIÓN DE CONEXIONES
# ============================================================================

def test_connections():
    """Tests de gestión de conexiones."""
    print("\n" + "=" * 80)
    print("TESTS GESTIÓN DE CONEXIONES (SAP HANA)")
    print("=" * 80)

    from hana import get_active_connections, get_connection_count

    result = TestResult()

    # Test GET_ACTIVE_CONNECTIONS
    def test_get_active_connections():
        conexiones = get_active_connections()
        assert len(conexiones) > 0, "Debe haber al menos 1 conexión activa"
        conn = conexiones[0]
        assert 'connection_id' in conn, "Debe tener connection_id"
        assert 'user_name' in conn, "Debe tener user_name"

    run_test(test_get_active_connections, "GET_ACTIVE_CONNECTIONS - Todas", result)

    # Test GET_CONNECTION_COUNT
    def test_get_connection_count():
        count = get_connection_count()
        assert count > 0, f"Debe haber al menos 1 conexión, hay {count}"

    run_test(test_get_connection_count, "GET_CONNECTION_COUNT - Total", result)

    # Información de conexiones
    print("\n  ℹ️  Información de conexiones actuales:")
    try:
        total = get_connection_count()
        print(f"      Total de conexiones en SAP HANA: {total}")

        conexiones = get_active_connections()
        users = {}
        for conn in conexiones:
            user = conn['user_name']
            users[user] = users.get(user, 0) + 1

        print("      Conexiones por usuario:")
        for user, count in sorted(users.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"        - {user}: {count}")
    except Exception as e:
        print(f"      Error obteniendo información: {e}")

    result.summary()
    return result.failed == 0


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                  MÓDULO SAP HANA - SUITE DE PRUEBAS                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

⚠️  ADVERTENCIA: Este script ejecutará operaciones en SAP HANA
   Solo ejecutar en ambiente de desarrollo

Este script ejecuta pruebas de:
- DML (Data Manipulation Language)
- DDL (Data Definition Language)
- DCL (Data Control Language)
- Gestión de Conexiones

Usando el schema: TEST_PYTHON
Servidor: Configurado en .env
    """)

    # Confirmar ejecución
    response = input("¿Desea continuar con los tests? (s/n): ")
    if response.lower() != 's':
        print("Tests cancelados por el usuario")
        sys.exit(0)

    # Tests
    all_passed = True

    try:
        # DML Tests
        if not test_dml():
            all_passed = False

        # DDL Tests
        if not test_ddl():
            all_passed = False

        # Conexiones Tests
        if not test_connections():
            all_passed = False

        # DCL Tests (opcional)
        response = input("\n¿Ejecutar tests DCL? (requiere permisos admin) (s/n): ")
        if response.lower() == 's':
            if not test_dcl():
                all_passed = False
        else:
            print("⚠️  Tests DCL omitidos")

    except Exception as e:
        print(f"\n❌ Error ejecutando tests: {e}")
        traceback.print_exc()
        all_passed = False

    # Resumen final
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON - Revisar logs arriba")
    print("=" * 80)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
