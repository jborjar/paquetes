"""
Script genérico MSSQL para importar/exportar estructura de tablas y vistas.

Exporta e importa la estructura completa (tablas + vistas) de bases de datos.

Uso:
    python -m paquetes.mssql_imp_exp_tbl_vw exp nombre_bd    # Exportar
    python -m paquetes.mssql_imp_exp_tbl_vw imp nombre_bd    # Importar

Funciones disponibles programáticamente:
- exportar_estructura(): Extrae estructura de tablas y vistas de una BD y genera archivo .def
- importar_estructura(): Lee archivo .def y replica estructura (tablas + vistas) en otra BD
"""
import sys
import os

# Agregar directorio padre al path para poder importar paquetes
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

from paquetes.mssql import (
    execute_query,
    get_table_columns,
    database_exists,
    create_database,
    drop_database,
    table_exists,
    create_table,
    execute_ddl
)


def exportar_estructura(database: str = 'progex', output_file: str = None):
    """
    Exporta la estructura de tablas y vistas de una base de datos a archivo .def

    Args:
        database: Nombre de la base de datos a extraer (default: 'progex')
        output_file: Ruta del archivo de salida (default: 'paquetes/tbl_vw.{database}.def')
    """

    # Generar nombre de archivo por defecto si no se proporciona
    if output_file is None:
        # Usar directorio donde está el script (paquetes/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, f'tbl_vw.{database}.def')

    print(f"Obteniendo tablas de la base de datos '{database}'...")

    # Obtener lista de tablas
    tablas_query = """
    SELECT
        TABLE_SCHEMA,
        TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA, TABLE_NAME
    """

    tablas = execute_query(tablas_query, database=database, fetch=True)
    print(f"Total tablas encontradas: {len(tablas)}")

    # Generar contenido del archivo
    output = []
    output.append('"""')
    output.append(f'Estructura de tablas de la base de datos {database}.')
    output.append('Generado automáticamente usando el módulo mssql.')
    output.append('"""')
    output.append('')
    output.append('TABLAS = {')

    for tabla in tablas:
        schema = tabla.TABLE_SCHEMA
        nombre = tabla.TABLE_NAME
        tabla_completa = f"{schema}.{nombre}"

        print(f"Procesando: {tabla_completa}")

        # Obtener columnas
        columnas = get_table_columns(nombre, database=database)

        # Obtener PKs
        pk_query = f"""
        SELECT kcu.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            AND tc.TABLE_NAME = kcu.TABLE_NAME
        WHERE tc.TABLE_SCHEMA = '{schema}'
            AND tc.TABLE_NAME = '{nombre}'
            AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ORDER BY kcu.ORDINAL_POSITION
        """

        pks = execute_query(pk_query, database=database, fetch=True)
        pk_columns = [pk.COLUMN_NAME for pk in pks]

        # Agregar tabla al output
        output.append(f'    "{tabla_completa}": {{')
        output.append(f'        "schema": "{schema}",')
        output.append(f'        "nombre": "{nombre}",')
        output.append(f'        "primary_keys": {pk_columns},')
        output.append(f'        "columnas": [')

        for col in columnas:
            nullable_str = "True" if col['is_nullable'] else "False"
            longitud = col['max_length'] if col['max_length'] else None
            default_val = col['default_value'] if col['default_value'] else None

            output.append(f'            {{')
            output.append(f'                "nombre": "{col["name"]}",')
            output.append(f'                "tipo": "{col["type"]}",')
            output.append(f'                "longitud": {longitud},')
            output.append(f'                "nullable": {nullable_str},')
            output.append(f'                "default": {repr(default_val)}')
            output.append(f'            }},')

        output.append(f'        ]')
        output.append(f'    }},')

    output.append('}')
    output.append('')

    # Obtener vistas
    print(f"\nObteniendo vistas de la base de datos '{database}'...")
    vistas_query = """
    SELECT
        TABLE_SCHEMA,
        TABLE_NAME,
        VIEW_DEFINITION
    FROM INFORMATION_SCHEMA.VIEWS
    ORDER BY TABLE_SCHEMA, TABLE_NAME
    """

    vistas = execute_query(vistas_query, database=database, fetch=True)
    print(f"Total vistas encontradas: {len(vistas)}")

    output.append('VISTAS = {')

    for vista in vistas:
        schema = vista.TABLE_SCHEMA
        nombre = vista.TABLE_NAME
        vista_completa = f"{schema}.{nombre}"
        definicion = vista.VIEW_DEFINITION

        print(f"Procesando vista: {vista_completa}")

        # Limpiar definición: remover CREATE VIEW ... AS del inicio si existe
        import re
        # Patrón para remover CREATE VIEW nombre AS
        patron = r'^\s*CREATE\s+VIEW\s+[\[\]a-zA-Z0-9_.]+\s+AS\s*'
        definicion_limpia = re.sub(patron, '', definicion, flags=re.IGNORECASE)

        # Agregar vista al output
        output.append(f'    "{vista_completa}": {{')
        output.append(f'        "schema": "{schema}",')
        output.append(f'        "nombre": "{nombre}",')
        output.append(f'        "definicion": {repr(definicion_limpia)}')
        output.append(f'    }},')

    output.append('}')
    output.append('')
    output.append('')
    output.append('def get_tabla_info(nombre_tabla: str) -> dict:')
    output.append('    """')
    output.append('    Obtiene información de una tabla.')
    output.append('    ')
    output.append('    Args:')
    output.append('        nombre_tabla: Nombre completo de la tabla (schema.nombre)')
    output.append('    ')
    output.append('    Returns:')
    output.append('        Diccionario con información de la tabla')
    output.append('    """')
    output.append('    return TABLAS.get(nombre_tabla)')
    output.append('')
    output.append('')
    output.append('def get_vista_info(nombre_vista: str) -> dict:')
    output.append('    """')
    output.append('    Obtiene información de una vista.')
    output.append('    ')
    output.append('    Args:')
    output.append('        nombre_vista: Nombre completo de la vista (schema.nombre)')
    output.append('    ')
    output.append('    Returns:')
    output.append('        Diccionario con información de la vista')
    output.append('    """')
    output.append('    return VISTAS.get(nombre_vista)')
    output.append('')
    output.append('')
    output.append('def listar_tablas() -> list:')
    output.append('    """Retorna lista de nombres de todas las tablas."""')
    output.append('    return list(TABLAS.keys())')
    output.append('')
    output.append('')
    output.append('def listar_vistas() -> list:')
    output.append('    """Retorna lista de nombres de todas las vistas."""')
    output.append('    return list(VISTAS.keys())')
    output.append('')

    # Escribir archivo
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n✓ Archivo generado: {output_file}")
    print(f"  Base de datos: {database}")
    print(f"  Total de tablas: {len(tablas)}")
    print(f"  Total de vistas: {len(vistas)}")
    print(f"  Total de líneas: {len(output)}")


def importar_estructura(
    database_destino: str,
    archivo_estructura: str = None,
    recrear_bd: bool = False
):
    """
    Importa la estructura de tablas desde un archivo .def a una base de datos.

    Args:
        database_destino: Nombre de la BD destino donde crear las tablas
        archivo_estructura: Ruta al archivo .def con estructura (ej: tbl_vw.progex.def).
                          Si no se proporciona, busca automáticamente en paquetes/
        recrear_bd: Si True, elimina y recrea la BD (default: False)
    """
    # Si no se proporciona archivo, buscar en paquetes/
    if archivo_estructura is None:
        import glob
        # Buscar en directorio donde está el script (paquetes/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        archivos_def = glob.glob(os.path.join(script_dir, 'tbl_vw.*.def'))

        if not archivos_def:
            raise FileNotFoundError(
                f"No se encontró ningún archivo .def en {script_dir}/\n"
                "Ejecuta primero: python -m paquetes.mssql_imp_exp_tbl_vw <nombre_bd>"
            )

        if len(archivos_def) > 1:
            print("⚠️  Se encontraron múltiples archivos .def:")
            for f in archivos_def:
                print(f"   - {f}")
            archivo_estructura = archivos_def[0]
            print(f"\n→ Usando: {archivo_estructura}")
        else:
            archivo_estructura = archivos_def[0]
            print(f"→ Archivo encontrado: {archivo_estructura}")

    print(f"\n=== Copiando estructura a '{database_destino}' ===\n")

    # 1. Crear o verificar base de datos
    print(f"1. Verificando base de datos '{database_destino}'...")
    if recrear_bd and database_exists(database_destino):
        print(f"   Eliminando BD existente...")
        drop_database(database_destino, force=True)

    if not database_exists(database_destino):
        print(f"   Creando base de datos '{database_destino}'...")
        create_database(database_destino)
        print(f"   ✓ Base de datos creada")
    else:
        print(f"   ✓ Base de datos ya existe")

    # 2. Cargar estructura desde archivo
    print(f"\n2. Cargando estructura desde '{archivo_estructura}'...")

    # Verificar que el archivo existe
    if not os.path.exists(archivo_estructura):
        raise FileNotFoundError(f"El archivo {archivo_estructura} no existe")

    # Leer y ejecutar el archivo .def como código Python
    with open(archivo_estructura, 'r', encoding='utf-8') as f:
        codigo = f.read()

    # Crear un namespace para ejecutar el código
    namespace = {}
    exec(codigo, namespace)

    TABLAS = namespace['TABLAS']
    print(f"   ✓ Estructura cargada: {len(TABLAS)} tablas encontradas")

    # 3. Verificar que no existan tablas antes de copiar
    print(f"\n3. Verificando que no existan tablas en '{database_destino}'...")
    tablas_existentes = []

    for nombre_completo, info in TABLAS.items():
        nombre_tabla = info['nombre']
        if table_exists(nombre_tabla, database=database_destino):
            tablas_existentes.append(nombre_completo)

    if tablas_existentes:
        print(f"   ✗ Error: Las siguientes tablas ya existen en '{database_destino}':")
        for tabla in tablas_existentes:
            print(f"      - {tabla}")
        raise Exception(
            f"\n{len(tablas_existentes)} tabla(s) ya existen en la base de datos.\n"
            f"Use --recrear para eliminar y recrear la BD, o elimine las tablas manualmente."
        )

    print(f"   ✓ No hay conflictos de tablas")

    # 4. Crear tablas
    print(f"\n4. Creando tablas en '{database_destino}'...")
    tablas_creadas = 0

    for nombre_completo, info in TABLAS.items():
        nombre_tabla = info['nombre']
        schema = info['schema']
        primary_keys = info['primary_keys']
        columnas = info['columnas']

        print(f"   → Creando {nombre_completo}...")

        # Construir definición de columnas
        columnas_def = {}
        for col in columnas:
            tipo = col['tipo'].upper()
            longitud = col['longitud']
            nullable = col['nullable']
            default = col['default']

            # Construir tipo con longitud
            if longitud and tipo in ('NVARCHAR', 'VARCHAR', 'CHAR', 'NCHAR', 'BINARY', 'VARBINARY'):
                if longitud == -1:  # MAX
                    tipo_completo = f"{tipo}(MAX)"
                else:
                    tipo_completo = f"{tipo}({longitud})"
            else:
                tipo_completo = tipo

            # Agregar NULL/NOT NULL
            if not nullable:
                tipo_completo += " NOT NULL"

            # Agregar DEFAULT si existe y no es NULL
            if default and default != 'NULL':
                # Limpiar el default de paréntesis extra de SQL Server
                default_limpio = default.strip('()')

                # Si es una función (sin comillas), usar tal cual
                if default_limpio.upper() in ('GETDATE', 'NEWID', 'GETUTCDATE', 'SYSDATETIME'):
                    tipo_completo += f" DEFAULT {default_limpio.upper()}()"
                else:
                    tipo_completo += f" DEFAULT {default_limpio}"

            columnas_def[col['nombre']] = tipo_completo

        # Crear tabla
        try:
            create_table(
                nombre_tabla,
                columnas_def,
                primary_key=primary_keys if primary_keys else None,
                database=database_destino
            )
            print(f"      ✓ Tabla creada con {len(columnas)} columnas")
            tablas_creadas += 1
        except Exception as e:
            print(f"      ✗ Error: {e}")

    # 5. Verificar que no existan vistas antes de copiar
    VISTAS = namespace.get('VISTAS', {})

    if VISTAS:
        print(f"\n5. Verificando que no existan vistas en '{database_destino}'...")
        vistas_existentes = []

        for nombre_completo, info in VISTAS.items():
            nombre_vista = info['nombre']
            schema = info['schema']

            # Verificar si vista ya existe
            check_query = f"""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.VIEWS
            WHERE TABLE_NAME = '{nombre_vista}' AND TABLE_SCHEMA = '{schema}'
            """
            resultado = execute_query(check_query, database=database_destino, fetch=True)

            if resultado and resultado[0].count > 0:
                vistas_existentes.append(nombre_completo)

        if vistas_existentes:
            print(f"   ✗ Error: Las siguientes vistas ya existen en '{database_destino}':")
            for vista in vistas_existentes:
                print(f"      - {vista}")
            raise Exception(
                f"\n{len(vistas_existentes)} vista(s) ya existen en la base de datos.\n"
                f"Use --recrear para eliminar y recrear la BD, o elimine las vistas manualmente."
            )

        print(f"   ✓ No hay conflictos de vistas")

    # 6. Crear vistas
    if not VISTAS:
        print(f"\n6. No hay vistas en el archivo para copiar")
        vistas_creadas = 0
    else:
        print(f"\n6. Creando vistas en '{database_destino}'...")
        vistas_creadas = 0

        for nombre_completo, info in VISTAS.items():
            nombre_vista = info['nombre']
            schema = info['schema']
            definicion = info['definicion']

            print(f"   → Creando {nombre_completo}...")

            try:
                # Crear vista con schema.nombre
                # La definición está limpia (solo SELECT), agregamos CREATE VIEW
                create_view_sql = f"CREATE VIEW {schema}.{nombre_vista} AS {definicion}"
                execute_ddl(create_view_sql, database=database_destino)
                print(f"      ✓ Vista creada")
                vistas_creadas += 1
            except Exception as e:
                print(f"      ✗ Error: {e}")

    # 7. Resumen
    print(f"\n=== Resumen ===")
    print(f"Archivo origen:        {archivo_estructura}")
    print(f"Base de datos destino: {database_destino}")
    print(f"Tablas creadas:        {tablas_creadas}")
    print(f"Vistas creadas:        {vistas_creadas}")
    print(f"Total procesadas:      {len(TABLAS)} tablas, {len(VISTAS)} vistas")
    print(f"\n✓ Proceso completado exitosamente")

    # 8. Eliminar archivo .def después de copia exitosa
    if os.path.exists(archivo_estructura):
        print(f"\n→ Eliminando archivo {archivo_estructura}...")
        os.remove(archivo_estructura)
        print(f"   ✓ Archivo eliminado")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Herramienta MSSQL para importar/exportar estructura de tablas y vistas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Exportar estructura de progex (genera paquetes/tbl_vw.progex.def)
  python -m paquetes.mssql_imp_exp_tbl_vw exp progex

  # Exportar con nombre personalizado (genera paquetes/mi_estructura.def)
  python -m paquetes.mssql_imp_exp_tbl_vw exp progex mi_estructura

  # Importar estructura a nueva BD (busca cualquier .def en paquetes/)
  python -m paquetes.mssql_imp_exp_tbl_vw imp test_db

  # Importar especificando archivo .def
  python -m paquetes.mssql_imp_exp_tbl_vw imp test_db tbl_vw.progex.def

  # Importar recreando la BD destino
  python -m paquetes.mssql_imp_exp_tbl_vw imp test_db --recrear
        """
    )

    subparsers = parser.add_subparsers(dest='comando', help='Comando a ejecutar', required=True)

    # Subcomando: exp (exportar)
    parser_exp = subparsers.add_parser(
        'exp',
        help='Exporta estructura de tablas y vistas a archivo .def'
    )
    parser_exp.add_argument(
        'database',
        help='Nombre de la base de datos a exportar'
    )
    parser_exp.add_argument(
        'nombre_salida',
        nargs='?',
        default=None,
        help='Nombre del archivo de salida (default: tbl_vw.{database}.def)'
    )

    # Subcomando: imp (importar)
    parser_imp = subparsers.add_parser(
        'imp',
        help='Importa estructura de tablas y vistas desde archivo .def'
    )
    parser_imp.add_argument(
        'database_destino',
        help='Nombre de la base de datos destino'
    )
    parser_imp.add_argument(
        'nombre_archivo',
        nargs='?',
        default=None,
        help='Nombre del archivo .def. Si no se especifica, busca cualquier .def en paquetes/'
    )
    parser_imp.add_argument(
        '--recrear',
        action='store_true',
        help='Eliminar y recrear la base de datos si existe'
    )

    args = parser.parse_args()

    try:
        if args.comando == 'exp':
            # Determinar nombre de archivo de salida
            script_dir = os.path.dirname(os.path.abspath(__file__))

            if args.nombre_salida:
                # Si se especificó nombre, agregar .def si no lo tiene
                nombre_archivo = args.nombre_salida if args.nombre_salida.endswith('.def') else f'{args.nombre_salida}.def'
            else:
                # Usar nombre por defecto
                nombre_archivo = f'tbl_vw.{args.database}.def'

            output_file = os.path.join(script_dir, nombre_archivo)
            exportar_estructura(database=args.database, output_file=output_file)

        elif args.comando == 'imp':
            # Determinar archivo de entrada
            script_dir = os.path.dirname(os.path.abspath(__file__))

            if args.nombre_archivo:
                # Si se especificó nombre de archivo, buscar en paquetes/
                archivo_estructura = os.path.join(script_dir, args.nombre_archivo)
            else:
                # Buscar automáticamente cualquier .def en paquetes/
                archivo_estructura = None

            importar_estructura(
                database_destino=args.database_destino,
                archivo_estructura=archivo_estructura,
                recrear_bd=args.recrear
            )
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
