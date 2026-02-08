"""
Script de pruebas para el módulo MSSQL.
Ejecuta tests de DML, DDL y DCL usando la base de datos 'test_python'.
"""
import sys
import os
import traceback
from typing import Callable

# Agregar el directorio padre al path para poder importar mssql
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
    print("TESTS DML - DATA MANIPULATION LANGUAGE")
    print("=" * 80)

    from mssql import (
        insert, insert_many, select, select_one,
        update, delete, exists, count, upsert
    )

    result = TestResult()
    test_db = 'test_python'

    # Test INSERT
    def test_insert():
        insert('test_clientes', {
            'nombre': 'Test Cliente 1',
            'email': 'test1@email.com',
            'telefono': '5551111111'
        }, database=test_db)

    run_test(test_insert, "INSERT - Insertar registro", result)

    # Test INSERT_MANY
    def test_insert_many():
        datos = [
            ('Test Cliente 2', 'test2@email.com', '5552222222'),
            ('Test Cliente 3', 'test3@email.com', '5553333333'),
            ('Test Cliente 4', 'test4@email.com', '5554444444')
        ]
        total = insert_many(
            'test_clientes',
            ['nombre', 'email', 'telefono'],
            datos,
            database=test_db
        )
        # pyodbc a veces retorna -1 con executemany, verificar que retorne algo
        assert total != 0, f"insert_many debe retornar un valor, retornó {total}"
        # Verificar que los registros se insertaron consultando
        from mssql import count
        total_registros = count('test_clientes', database=test_db)
        assert total_registros >= 4, f"Debe haber al menos 4 registros después de insert_many, hay {total_registros}"

    run_test(test_insert_many, "INSERT_MANY - Inserción masiva", result)

    # Test SELECT
    def test_select():
        registros = select('test_clientes', database=test_db)
        assert len(registros) >= 4, f"Se esperaban al menos 4 registros, se obtuvieron {len(registros)}"

    run_test(test_select, "SELECT - Consultar registros", result)

    # Test SELECT con filtros
    def test_select_filtered():
        registros = select(
            'test_clientes',
            where='activo = ?',
            where_params=(1,),
            database=test_db
        )
        assert len(registros) >= 1, "Debe haber al menos 1 registro activo"

    run_test(test_select_filtered, "SELECT - Con filtros", result)

    # Test SELECT_ONE
    def test_select_one():
        registro = select_one(
            'test_clientes',
            where='nombre = ?',
            where_params=('Test Cliente 1',),
            database=test_db
        )
        assert registro is not None, "Debe encontrar el registro"
        assert registro.nombre == 'Test Cliente 1', "El nombre debe coincidir"

    run_test(test_select_one, "SELECT_ONE - Consultar un registro", result)

    # Test EXISTS
    def test_exists():
        existe = exists(
            'test_clientes',
            where='email = ?',
            where_params=('test1@email.com',),
            database=test_db
        )
        assert existe, "El registro debe existir"

    run_test(test_exists, "EXISTS - Verificar existencia", result)

    # Test COUNT
    def test_count():
        total = count('test_clientes', database=test_db)
        assert total >= 4, f"Debe haber al menos 4 registros, hay {total}"

    run_test(test_count, "COUNT - Contar registros", result)

    # Test UPDATE
    def test_update():
        rows = update(
            'test_clientes',
            data={'telefono': '5559999999'},
            where='nombre = ?',
            where_params=('Test Cliente 1',),
            database=test_db
        )
        assert rows == 1, f"Debe actualizar 1 registro, actualizó {rows}"

    run_test(test_update, "UPDATE - Actualizar registros", result)

    # Test UPSERT (INSERT) - Sin especificar ID para evitar problema con IDENTITY
    def test_upsert_insert():
        # Primero insertar sin upsert para tener un email único
        insert('test_clientes', {
            'nombre': 'Test Upsert Original',
            'email': 'upsert_test@email.com',
            'telefono': '5558888888'
        }, database=test_db)

        # Ahora hacer upsert usando email como key
        rowcount, operation = upsert(
            'test_clientes',
            data={
                'nombre': 'Test Upsert Updated',
                'email': 'upsert_test@email.com',
                'telefono': '5559999999',
                'activo': 1
            },
            key_columns=['email'],
            database=test_db
        )
        assert operation == 'updated', f"Debe ser UPDATE, fue {operation}"

    run_test(test_upsert_insert, "UPSERT - Update por key natural", result)

    # Test DELETE
    def test_delete():
        rows = delete(
            'test_clientes',
            where='email = ?',
            where_params=('upsert_test@email.com',),
            database=test_db
        )
        assert rows == 1, f"Debe eliminar 1 registro, eliminó {rows}"

    run_test(test_delete, "DELETE - Eliminar registros", result)

    result.summary()
    return result.failed == 0


# ============================================================================
# TESTS DDL
# ============================================================================

def test_ddl():
    """Tests de Data Definition Language."""
    print("\n" + "=" * 80)
    print("TESTS DDL - DATA DEFINITION LANGUAGE")
    print("=" * 80)

    from mssql import (
        database_exists, create_database, drop_database,
        table_exists, create_table, drop_table,
        create_index, drop_index, execute_ddl,
        get_table_columns, truncate_table
    )

    result = TestResult()
    test_db = 'test_python'

    # Test DATABASE_EXISTS
    def test_database_exists():
        existe = database_exists(test_db)
        assert existe, f"La BD '{test_db}' debe existir"

    run_test(test_database_exists, "DATABASE_EXISTS - Verificar BD", result)

    # Test TABLE_EXISTS
    def test_table_exists():
        existe = table_exists('test_clientes', database=test_db)
        assert existe, "La tabla 'test_clientes' debe existir"

    run_test(test_table_exists, "TABLE_EXISTS - Verificar tabla", result)

    # Test CREATE_TABLE (nueva)
    def test_create_table():
        created = create_table(
            'test_productos',
            {
                'id': 'INT IDENTITY(1,1)',
                'codigo': 'NVARCHAR(50) NOT NULL',
                'nombre': 'NVARCHAR(100)',
                'precio': 'DECIMAL(18,2)',
                'activo': 'BIT DEFAULT 1'
            },
            primary_key='id',
            database=test_db
        )
        assert created, "La tabla debe crearse exitosamente"

    run_test(test_create_table, "CREATE_TABLE - Crear tabla", result)

    # Test GET_TABLE_COLUMNS
    def test_get_table_columns():
        columnas = get_table_columns('test_productos', database=test_db)
        assert len(columnas) >= 5, f"Debe haber al menos 5 columnas, hay {len(columnas)}"
        nombres = [c['name'] for c in columnas]
        assert 'id' in nombres, "Debe existir columna 'id'"
        assert 'nombre' in nombres, "Debe existir columna 'nombre'"

    run_test(test_get_table_columns, "GET_TABLE_COLUMNS - Estructura", result)

    # Test CREATE_INDEX
    def test_create_index():
        created = create_index(
            'test_productos',
            'idx_codigo',
            'codigo',
            database=test_db
        )
        assert created, "El índice debe crearse exitosamente"

    run_test(test_create_index, "CREATE_INDEX - Crear índice", result)

    # Test EXECUTE_DDL (crear vista)
    def test_execute_ddl():
        execute_ddl('''
            CREATE OR ALTER VIEW vw_test_productos_activos AS
            SELECT id, codigo, nombre, precio
            FROM test_productos
            WHERE activo = 1
        ''', database=test_db)

    run_test(test_execute_ddl, "EXECUTE_DDL - DDL personalizado", result)

    # Test TRUNCATE_TABLE (necesita datos primero)
    def test_truncate_table():
        from mssql import insert
        # Insertar datos de prueba
        insert('test_productos', {
            'codigo': 'PROD001',
            'nombre': 'Producto Test',
            'precio': 100.00
        }, database=test_db)

        # Truncar
        truncate_table('test_productos', database=test_db)

        # Verificar que está vacía
        from mssql import count
        total = count('test_productos', database=test_db)
        assert total == 0, f"La tabla debe estar vacía, tiene {total} registros"

    run_test(test_truncate_table, "TRUNCATE_TABLE - Vaciar tabla", result)

    # Test DROP_INDEX
    def test_drop_index():
        deleted = drop_index('test_productos', 'idx_codigo', database=test_db)
        assert deleted, "El índice debe eliminarse exitosamente"

    run_test(test_drop_index, "DROP_INDEX - Eliminar índice", result)

    # Test DROP_TABLE
    def test_drop_table():
        deleted = drop_table('test_productos', database=test_db)
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
    print("TESTS DCL - DATA CONTROL LANGUAGE")
    print("=" * 80)
    print("⚠️  Requiere permisos de administrador\n")

    from mssql import (
        login_exists, create_login, drop_login,
        user_exists, create_user, drop_user,
        grant_permission, get_user_permissions,
        create_role, add_user_to_role, get_user_roles
    )

    result = TestResult()
    test_db = 'test_python'

    # Test CREATE_LOGIN
    def test_create_login():
        # Eliminar si existe
        if login_exists('test_user'):
            drop_login('test_user')

        created = create_login('test_user', 'TestPass123!', default_database=test_db)
        assert created, "El login debe crearse exitosamente"

    run_test(test_create_login, "CREATE_LOGIN - Crear login", result)

    # Test LOGIN_EXISTS
    def test_login_exists():
        existe = login_exists('test_user')
        assert existe, "El login 'test_user' debe existir"

    run_test(test_login_exists, "LOGIN_EXISTS - Verificar login", result)

    # Test CREATE_USER
    def test_create_user():
        # Eliminar si existe
        if user_exists('test_user', database=test_db):
            drop_user('test_user', database=test_db)

        created = create_user('test_user', database=test_db)
        assert created, "El usuario debe crearse exitosamente"

    run_test(test_create_user, "CREATE_USER - Crear usuario", result)

    # Test USER_EXISTS
    def test_user_exists():
        existe = user_exists('test_user', database=test_db)
        assert existe, "El usuario 'test_user' debe existir"

    run_test(test_user_exists, "USER_EXISTS - Verificar usuario", result)

    # Test GRANT_PERMISSION
    def test_grant_permission():
        grant_permission('SELECT', 'test_clientes', 'test_user', database=test_db)

    run_test(test_grant_permission, "GRANT_PERMISSION - Otorgar permiso", result)

    # Test GET_USER_PERMISSIONS
    def test_get_user_permissions():
        permisos = get_user_permissions('test_user', database=test_db)
        assert len(permisos) > 0, "Debe tener al menos 1 permiso"

    run_test(test_get_user_permissions, "GET_USER_PERMISSIONS - Consultar permisos", result)

    # Test ADD_USER_TO_ROLE
    def test_add_user_to_role():
        add_user_to_role('test_user', 'db_datareader', database=test_db)

    run_test(test_add_user_to_role, "ADD_USER_TO_ROLE - Agregar a rol", result)

    # Test GET_USER_ROLES
    def test_get_user_roles():
        roles = get_user_roles('test_user', database=test_db)
        assert 'db_datareader' in roles, "Debe tener el rol 'db_datareader'"

    run_test(test_get_user_roles, "GET_USER_ROLES - Consultar roles", result)

    # Cleanup
    def test_cleanup():
        drop_user('test_user', database=test_db)
        drop_login('test_user')

    run_test(test_cleanup, "CLEANUP - Limpiar usuarios y logins", result)

    result.summary()
    return result.failed == 0


# ============================================================================
# TESTS GESTIÓN DE CONEXIONES
# ============================================================================

def test_connections():
    """Tests de gestión de conexiones."""
    print("\n" + "=" * 80)
    print("TESTS GESTIÓN DE CONEXIONES")
    print("=" * 80)

    from mssql import (
        get_active_connections,
        get_connection_count,
        kill_connection,
        kill_all_connections
    )

    result = TestResult()
    test_db = 'test_python'

    # Test GET_ACTIVE_CONNECTIONS (todas)
    def test_get_active_connections_all():
        conexiones = get_active_connections()
        assert len(conexiones) > 0, "Debe haber al menos 1 conexión activa"
        # Verificar estructura del resultado
        conn = conexiones[0]
        assert 'session_id' in conn, "Debe tener session_id"
        assert 'login_name' in conn, "Debe tener login_name"
        assert 'database_name' in conn, "Debe tener database_name"

    run_test(test_get_active_connections_all, "GET_ACTIVE_CONNECTIONS - Todas", result)

    # Test GET_ACTIVE_CONNECTIONS (por BD)
    def test_get_active_connections_db():
        conexiones = get_active_connections(database=test_db)
        # Puede o no haber conexiones a 'test_python'
        assert isinstance(conexiones, list), "Debe retornar una lista"

    run_test(test_get_active_connections_db, "GET_ACTIVE_CONNECTIONS - Por BD", result)

    # Test GET_CONNECTION_COUNT (todas)
    def test_get_connection_count_all():
        count = get_connection_count()
        assert count > 0, f"Debe haber al menos 1 conexión, hay {count}"

    run_test(test_get_connection_count_all, "GET_CONNECTION_COUNT - Todas", result)

    # Test GET_CONNECTION_COUNT (por BD)
    def test_get_connection_count_db():
        count = get_connection_count(test_db)
        assert count >= 0, "Debe retornar un número >= 0"

    run_test(test_get_connection_count_db, "GET_CONNECTION_COUNT - Por BD", result)

    # Test KILL_ALL_CONNECTIONS (BD de prueba)
    def test_kill_all_connections():
        from mssql import database_exists, create_database, drop_database

        test_conn_db = 'test_connections_kill'

        try:
            # Crear BD temporal
            if database_exists(test_conn_db):
                drop_database(test_conn_db, force=True)
            create_database(test_conn_db)

            # Cerrar conexiones (debe ser 0 porque recién se creó)
            closed = kill_all_connections(test_conn_db, exclude_current=True)
            assert closed >= 0, "Debe retornar un número >= 0"

            # Limpiar
            drop_database(test_conn_db, force=True)

        except Exception as e:
            # Intentar limpiar
            try:
                if database_exists(test_conn_db):
                    drop_database(test_conn_db, force=True)
            except:
                pass
            raise e

    run_test(test_kill_all_connections, "KILL_ALL_CONNECTIONS - Cerrar todas", result)

    # Test monitoreo de conexiones (informativo)
    print("\n  ℹ️  Información de conexiones actuales:")
    try:
        total = get_connection_count()
        print(f"      Total de conexiones en el servidor: {total}")

        # Agrupar por base de datos
        conexiones = get_active_connections()
        db_counts = {}
        for conn in conexiones:
            db = conn['database_name'] or 'NULL'
            db_counts[db] = db_counts.get(db, 0) + 1

        print("      Conexiones por base de datos:")
        for db, count in sorted(db_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"        - {db}: {count}")
    except Exception as e:
        print(f"      Error obteniendo información: {e}")

    result.summary()
    return result.failed == 0


# ============================================================================
# SETUP Y TEARDOWN
# ============================================================================

def setup_test_environment():
    """Configura el ambiente de pruebas."""
    print("\n" + "=" * 80)
    print("CONFIGURACIÓN DEL AMBIENTE DE PRUEBAS")
    print("=" * 80)

    from mssql import (
        database_exists, create_database, drop_database,
        table_exists, create_table
    )

    test_db = 'test_python'

    try:
        # Crear BD si no existe
        print("\n1. Verificando base de datos 'test_python'...")
        if not database_exists(test_db):
            print("   Creando base de datos 'test_python'...")
            create_database(test_db)
            print("   ✓ Base de datos creada")
        else:
            print("   ✓ Base de datos ya existe")

        # Crear tabla test_clientes
        print("\n2. Verificando tabla 'test_clientes'...")
        if table_exists('test_clientes', database=test_db):
            print("   Tabla ya existe, limpiando...")
            from mssql import truncate_table
            truncate_table('test_clientes', database=test_db)
        else:
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
                database=test_db
            )
        print("   ✓ Tabla lista")

        print("\n✓ Ambiente de pruebas configurado correctamente")
        return True

    except Exception as e:
        print(f"\n❌ Error configurando ambiente: {e}")
        traceback.print_exc()
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    MÓDULO MSSQL - SUITE DE PRUEBAS                        ║
╚═══════════════════════════════════════════════════════════════════════════╝

Este script ejecuta pruebas de:
- DML (Data Manipulation Language)
- DDL (Data Definition Language)
- DCL (Data Control Language)

Usando la base de datos: test
Servidor: mssql-api-mcp
    """)

    # Setup
    if not setup_test_environment():
        print("\n❌ No se pudo configurar el ambiente de pruebas")
        sys.exit(1)

    # Tests
    all_passed = True

    try:
        # DML Tests
        if not test_dml():
            all_passed = False

        # DDL Tests
        if not test_ddl():
            all_passed = False

        # Gestión de Conexiones Tests
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
