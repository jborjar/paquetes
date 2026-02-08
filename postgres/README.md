# Módulo PostgreSQL - Documentación Completa

Biblioteca completa para operaciones con PostgreSQL que sigue el estándar SQL dividiendo las funciones en tres categorías principales: DML, DDL y DCL.

> ⚠️ **MÓDULO GENÉRICO**: Este módulo NO tiene valores por defecto hardcodeados. El usuario debe proporcionar TODAS las variables de conexión en el archivo `.env`. Ver [CONFIG.md](../README.md#-configuración) para más detalles.

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Instalación y Configuración](#instalación-y-configuración)
- [Estructura del Módulo](#estructura-del-módulo)
- [DML - Data Manipulation Language](#dml---data-manipulation-language)
- [DDL - Data Definition Language](#ddl---data-definition-language)
- [DCL - Data Control Language](#dcl---data-control-language)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Referencia Rápida](#referencia-rápida)
- [Mejores Prácticas](#mejores-prácticas)

---

## Descripción General

El módulo PostgreSQL proporciona una interfaz Python de alto nivel para interactuar con PostgreSQL, organizando las operaciones según el estándar SQL:

- **DML (Data Manipulation Language)**: Operaciones para manipular datos (INSERT, SELECT, UPDATE, DELETE)
- **DDL (Data Definition Language)**: Operaciones para definir estructuras (CREATE, DROP, ALTER)
- **DCL (Data Control Language)**: Operaciones para control de acceso (GRANT, REVOKE, roles)

### Características principales

- Interfaz simplificada basada en psycopg2
- Manejo automático de conexiones
- Soporte para operaciones por lotes
- Funciones parametrizadas para prevenir inyección SQL
- Gestión completa de roles y permisos
- Operaciones UPSERT nativas (INSERT ... ON CONFLICT)
- Soporte completo para schemas
- Retorna resultados como diccionarios

---

## Instalación y Configuración

### Requisitos

```bash
pip install psycopg2-binary
# O para compilar desde fuentes
pip install psycopg2
```

### Configuración de variables de entorno

⚠️ **El módulo es completamente genérico y NO tiene valores por defecto**.

El usuario DEBE configurar las siguientes variables en el archivo `.env`:

```env
# PostgreSQL (REQUERIDO - Sin valores por defecto)
POSTGRES_HOST=tu_servidor
POSTGRES_PORT=5432
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password
POSTGRES_DATABASE=tu_base_datos
```

**Nota**: Si alguna variable no está configurada, el módulo fallará al intentar conectarse. Ver [CONFIG.md](../README.md#-configuración) para documentación completa de configuración.

### Importación del módulo

```python
# Importar todas las funciones
from postgres import *

# O importar funciones específicas
from postgres import select, insert, create_table, grant_table_privileges
```

---

## Estructura del Módulo

```
postgres/
├── __init__.py           # Exporta todas las funciones públicas
├── postgres_dml.py       # Funciones DML (manipulación de datos)
├── postgres_ddl.py       # Funciones DDL (definición de estructura)
└── postgres_dcl.py       # Funciones DCL (control de acceso)
```

**Total de funciones**: 43 funciones

---

## DML - Data Manipulation Language

Funciones para manipular datos en tablas existentes.

### Conexión a la base de datos

#### `get_postgres_connection(database=None, host=None, port=None, user=None, password=None)`

Obtiene una conexión activa a PostgreSQL.

**Parámetros:**
- `database` (str, opcional): Nombre de la base de datos
- `host` (str, opcional): Host del servidor
- `port` (int, opcional): Puerto del servidor
- `user` (str, opcional): Usuario
- `password` (str, opcional): Contraseña

**Retorna:** Objeto `psycopg2.connection`

**Ejemplo:**
```python
conn = get_postgres_connection()
conn = get_postgres_connection(database='otra_bd')
```

---

### Inserción de datos

#### `insert(table, data, database=None, schema=None, returning=None)`

Inserta un registro en una tabla.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `data` (dict): Diccionario con columnas y valores `{columna: valor}`
- `database` (str, opcional): Base de datos opcional
- `schema` (str, opcional): Schema opcional (default: public)
- `returning` (str, opcional): Columna a retornar (ej: 'id' para obtener ID insertado)

**Retorna:** Valor de columna especificada en returning, o número de filas insertadas

**Ejemplo:**
```python
# Inserción simple
insert('empresas', {
    'nombre': 'Empresa 01',
    'activo': True,
    'codigo': 'EMP01'
})

# Con RETURNING para obtener ID generado
nuevo_id = insert('empresas', {
    'nombre': 'Empresa 02'
}, returning='id')
```

#### `insert_many(table, columns, values_list, database=None, schema=None, batch_size=1000)`

Inserta múltiples registros por lotes (más eficiente para grandes volúmenes).

**Parámetros:**
- `table` (str): Nombre de la tabla
- `columns` (list): Lista de nombres de columnas
- `values_list` (list): Lista de tuplas con valores
- `database` (str, opcional): Base de datos opcional
- `schema` (str, opcional): Schema opcional
- `batch_size` (int): Tamaño del lote (default: 1000)

**Retorna:** Total de filas insertadas

**Ejemplo:**
```python
insert_many(
    'proveedores',
    ['codigo', 'nombre', 'activo'],
    [
        ('P001', 'Proveedor 1', True),
        ('P002', 'Proveedor 2', True),
    ]
)
```

---

### Consulta de datos

#### `select(table, columns=None, where=None, where_params=None, order_by=None, limit=None, offset=None, database=None, schema=None)`

Consulta registros de una tabla.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `columns` (list, opcional): Lista de columnas a seleccionar (None = todas)
- `where` (str, opcional): Cláusula WHERE (sin la palabra WHERE)
- `where_params` (tuple, opcional): Tupla con parámetros para WHERE
- `order_by` (str, opcional): Cláusula ORDER BY
- `limit` (int, opcional): Número máximo de registros
- `offset` (int, opcional): Número de registros a saltar
- `database` (str, opcional): Base de datos opcional
- `schema` (str, opcional): Schema opcional

**Retorna:** Lista de diccionarios con los resultados

**Ejemplo:**
```python
# Seleccionar todo
select('empresas')

# Con filtros
empresas = select(
    'empresas',
    columns=['nombre', 'activo'],
    where='activo = %s',
    where_params=(True,),
    order_by='nombre',
    limit=10
)

for empresa in empresas:
    print(empresa['nombre'])
```

#### `select_one(table, columns=None, where=None, where_params=None, database=None, schema=None)`

Consulta un solo registro de una tabla.

**Retorna:** Diccionario con la primera fila encontrada o None

**Ejemplo:**
```python
empresa = select_one(
    'empresas',
    where='codigo = %s',
    where_params=('EMP01',)
)
if empresa:
    print(empresa['nombre'])
```

---

### Actualización de datos

#### `update(table, data, where, where_params, database=None, schema=None)`

Actualiza registros en una tabla.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `data` (dict): Diccionario con columnas y nuevos valores
- `where` (str): Cláusula WHERE (sin la palabra WHERE)
- `where_params` (tuple): Tupla con parámetros para WHERE
- `database` (str, opcional): Base de datos opcional
- `schema` (str, opcional): Schema opcional

**Retorna:** Número de filas actualizadas

**Ejemplo:**
```python
update(
    'empresas',
    {'activo': False},
    where='codigo = %s',
    where_params=('EMP01',)
)
```

---

### Eliminación de datos

#### `delete(table, where, where_params, database=None, schema=None)`

Elimina registros de una tabla.

**Retorna:** Número de filas eliminadas

**Ejemplo:**
```python
delete(
    'empresas',
    where='activo = %s AND fecha < %s',
    where_params=(False, '2020-01-01')
)
```

---

### Operaciones auxiliares

#### `exists(table, where, where_params, database=None, schema=None)`

Verifica si existe al menos un registro que cumpla una condición.

**Retorna:** True si existe, False si no

**Ejemplo:**
```python
if exists('empresas', 'codigo = %s', ('EMP01',)):
    print("La empresa existe")
```

#### `count(table, where=None, where_params=None, database=None, schema=None)`

Cuenta registros en una tabla.

**Retorna:** Número de registros

**Ejemplo:**
```python
total = count('empresas')
activas = count('empresas', 'activo = %s', (True,))
```

#### `upsert(table, data, conflict_columns, update_columns=None, database=None, schema=None)`

Inserta o actualiza un registro (INSERT ... ON CONFLICT).

**Parámetros:**
- `table` (str): Nombre de la tabla
- `data` (dict): Diccionario con columnas y valores
- `conflict_columns` (list): Columnas que determinan el conflicto
- `update_columns` (list, opcional): Columnas a actualizar en caso de conflicto
- `database` (str, opcional): Base de datos opcional
- `schema` (str, opcional): Schema opcional

**Retorna:** Número de filas afectadas

**Ejemplo:**
```python
upsert(
    'empresas',
    {'codigo': 'EMP01', 'nombre': 'Empresa 01', 'activo': True},
    conflict_columns=['codigo'],
    update_columns=['nombre', 'activo']
)
```

#### `execute_query(query, params=None, database=None, fetch=True)`

Ejecuta una consulta SQL personalizada.

**Retorna:** Lista de diccionarios con resultados (si fetch=True) o número de filas afectadas

**Ejemplo:**
```python
# Consulta SELECT
results = execute_query(
    "SELECT * FROM empresas WHERE activo = %s",
    (True,)
)

# Consulta UPDATE
affected = execute_query(
    "UPDATE empresas SET activo = %s WHERE codigo = %s",
    (False, 'EMP01'),
    fetch=False
)
```

---

## DDL - Data Definition Language

Funciones para crear y modificar la estructura de bases de datos, schemas y tablas.

⚠️ **ADVERTENCIA**: Las operaciones DDL modifican la estructura de la base de datos y pueden ser irreversibles. Usar con precaución.

### Gestión de Bases de Datos

#### `database_exists(database, host=None)`

Verifica si una base de datos existe.

**Retorna:** True si existe, False si no

#### `create_database(database, owner=None, encoding='UTF8', if_not_exists=True)`

Crea una base de datos.

**Ejemplo:**
```python
create_database('mi_base', owner='mi_usuario')
```

#### `drop_database(database, if_exists=True, force=False)`

Elimina una base de datos. ⚠️ IRREVERSIBLE

**Parámetros:**
- `force` (bool): Si True, cierra todas las conexiones activas antes de eliminar

#### `recreate_database(database, owner=None)`

Elimina y recrea una base de datos desde cero. ⚠️ ELIMINA TODOS LOS DATOS

---

### Gestión de Schemas

#### `schema_exists(schema, database=None)`

Verifica si un schema existe.

#### `create_schema(schema, authorization=None, if_not_exists=True, database=None)`

Crea un schema.

**Ejemplo:**
```python
create_schema('ventas', authorization='app_user')
```

#### `drop_schema(schema, if_exists=True, cascade=False, database=None)`

Elimina un schema.

**Parámetros:**
- `cascade` (bool): Si True, elimina también todos los objetos contenidos

---

### Gestión de Tablas

#### `table_exists(table, database=None, schema='public')`

Verifica si una tabla existe.

#### `create_table(table, columns, primary_key=None, if_not_exists=True, database=None, schema=None)`

Crea una tabla.

**Ejemplo:**
```python
create_table(
    'empresas',
    {
        'id': 'SERIAL',
        'codigo': 'VARCHAR(50) UNIQUE NOT NULL',
        'nombre': 'VARCHAR(200) NOT NULL',
        'activo': 'BOOLEAN DEFAULT TRUE',
        'fecha_registro': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    },
    primary_key='id'
)
```

#### `drop_table(table, if_exists=True, cascade=False, database=None, schema=None)`

Elimina una tabla. ⚠️ IRREVERSIBLE

#### `truncate_table(table, restart_identity=False, cascade=False, database=None, schema=None)`

Elimina todos los registros de una tabla.

**Parámetros:**
- `restart_identity` (bool): Si True, reinicia las secuencias
- `cascade` (bool): Si True, trunca también tablas referenciadas

---

### Gestión de Índices

#### `create_index(index_name, table, columns, unique=False, if_not_exists=True, method=None, database=None, schema=None)`

Crea un índice en una tabla.

**Parámetros:**
- `method` (str, opcional): Método del índice (btree, hash, gist, gin, etc.)

**Ejemplo:**
```python
create_index('idx_empresas_codigo', 'empresas', 'codigo', unique=True)
create_index('idx_empresas_nombre', 'empresas', ['nombre', 'activo'])
```

#### `drop_index(index_name, if_exists=True, cascade=False, database=None, schema=None)`

Elimina un índice.

---

## DCL - Data Control Language

Funciones para control de acceso y permisos.

⚠️ **ADVERTENCIA**: Las operaciones DCL modifican permisos y seguridad. Solo deben ser ejecutadas por administradores.

**Nota**: En PostgreSQL, usuarios y roles son equivalentes. Un usuario es un rol con privilegio LOGIN.

### Gestión de Roles y Usuarios

#### `role_exists(role_name, database=None)`

Verifica si un rol existe.

#### `create_role(role_name, password=None, login=True, superuser=False, createdb=False, createrole=False, if_not_exists=True, database=None)`

Crea un rol.

**Ejemplo:**
```python
# Crear usuario normal
create_role('app_user', 'P@ssw0rd!123')

# Crear usuario con privilegios
create_role('admin_user', 'Admin123!', createdb=True, createrole=True)
```

#### `create_user(username, password, createdb=False, createrole=False, if_not_exists=True, database=None)`

Crea un usuario (alias conveniente para create_role con LOGIN).

#### `drop_role(role_name, if_exists=True, database=None)`

Elimina un rol.

#### `alter_role_password(role_name, new_password, database=None)`

Cambia la contraseña de un rol.

---

### Gestión de Permisos

#### `grant_database_privileges(role_name, database, privileges='ALL', admin_database=None)`

Otorga privilegios sobre una base de datos.

**Privilegios disponibles**: ALL, CONNECT, CREATE, TEMPORARY, TEMP

**Ejemplo:**
```python
grant_database_privileges('app_user', 'mi_base', 'CONNECT')
```

#### `grant_schema_privileges(role_name, schema, privileges='ALL', database=None)`

Otorga privilegios sobre un schema.

**Privilegios disponibles**: ALL, CREATE, USAGE

#### `grant_table_privileges(role_name, table, privileges='ALL', schema='public', database=None)`

Otorga privilegios sobre una tabla.

**Privilegios disponibles**: ALL, SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER

**Ejemplo:**
```python
grant_table_privileges('app_user', 'empresas', 'ALL')
grant_table_privileges('readonly', 'empresas', ['SELECT'])
```

#### `grant_all_tables_in_schema(role_name, schema, privileges='ALL', database=None)`

Otorga privilegios sobre todas las tablas de un schema.

**Ejemplo:**
```python
grant_all_tables_in_schema('readonly', 'public', 'SELECT')
```

#### `grant_role_to_user(role_name, user_name, database=None)`

Otorga un rol a un usuario.

**Ejemplo:**
```python
grant_role_to_user('read_only', 'app_user')
```

---

### Utilidades de Seguridad

#### `create_readonly_user(username, password, database, schema='public')`

Crea un usuario con permisos de solo lectura en un schema.

**Ejemplo:**
```python
create_readonly_user('readonly', 'Pass123!', 'mi_base')
```

#### `create_readwrite_user(username, password, database, schema='public')`

Crea un usuario con permisos de lectura y escritura en un schema.

**Ejemplo:**
```python
create_readwrite_user('app_user', 'Pass123!', 'mi_base')
```

---

### Gestión de Conexiones

#### `get_active_connections(database=None)`

Obtiene las conexiones activas.

**Retorna:** Lista de diccionarios con información de conexiones

#### `get_connection_count(database=None)`

Obtiene el número de conexiones activas.

#### `terminate_connection(pid, database=None)`

Termina una conexión específica.

#### `terminate_all_connections(database, exclude_current=True)`

Termina todas las conexiones a una base de datos.

---

## Ejemplos de Uso

### Ejemplo 1: CRUD Completo

```python
from postgres import *

# Crear tabla
create_table(
    'productos',
    {
        'id': 'SERIAL',
        'codigo': 'VARCHAR(50) UNIQUE NOT NULL',
        'nombre': 'VARCHAR(200) NOT NULL',
        'precio': 'DECIMAL(10,2)',
        'stock': 'INTEGER DEFAULT 0',
        'activo': 'BOOLEAN DEFAULT TRUE'
    },
    primary_key='id'
)

# Insertar datos
insert('productos', {
    'codigo': 'PROD001',
    'nombre': 'Producto 1',
    'precio': 99.99,
    'stock': 10
})

# Insertar con RETURNING
nuevo_id = insert('productos', {
    'codigo': 'PROD002',
    'nombre': 'Producto 2',
    'precio': 149.99
}, returning='id')

# Consultar
productos = select(
    'productos',
    where='activo = %s AND precio < %s',
    where_params=(True, 200),
    order_by='nombre'
)

for producto in productos:
    print(f"{producto['codigo']}: {producto['nombre']} - ${producto['precio']}")

# Actualizar
update(
    'productos',
    {'precio': 89.99},
    where='codigo = %s',
    where_params=('PROD001',)
)

# Eliminar
delete('productos', where='stock = %s', where_params=(0,))
```

### Ejemplo 2: Uso de UPSERT

```python
# Insertar o actualizar si existe
upsert(
    'productos',
    {
        'codigo': 'PROD001',
        'nombre': 'Producto Actualizado',
        'precio': 119.99,
        'stock': 15
    },
    conflict_columns=['codigo'],
    update_columns=['nombre', 'precio', 'stock']
)
```

### Ejemplo 3: Gestión de Usuarios y Permisos

```python
# Crear base de datos
create_database('mi_aplicacion')

# Crear schema
create_schema('ventas', database='mi_aplicacion')

# Crear usuario de solo lectura
create_readonly_user('usuario_lectura', 'Pass123!', 'mi_aplicacion', 'ventas')

# Crear usuario con permisos completos
create_readwrite_user('usuario_app', 'AppPass456!', 'mi_aplicacion', 'ventas')
```

---

## Referencia Rápida

### Funciones DML (13 funciones)

| Función | Descripción |
|---------|-------------|
| `get_postgres_connection()` | Obtiene conexión a PostgreSQL |
| `insert()` | Inserta un registro |
| `insert_many()` | Inserta múltiples registros por lotes |
| `select()` | Consulta registros |
| `select_one()` | Consulta un registro |
| `update()` | Actualiza registros |
| `delete()` | Elimina registros |
| `exists()` | Verifica si existe un registro |
| `count()` | Cuenta registros |
| `execute_query()` | Ejecuta query personalizada |
| `upsert()` | INSERT ... ON CONFLICT |
| `truncate()` | Elimina todos los registros |
| `get_table_columns()` | Obtiene columnas de una tabla |

### Funciones DDL (15 funciones)

| Función | Descripción |
|---------|-------------|
| `database_exists()` | Verifica si existe una BD |
| `create_database()` | Crea una base de datos |
| `drop_database()` | Elimina una base de datos |
| `recreate_database()` | Recrea una base de datos |
| `schema_exists()` | Verifica si existe un schema |
| `create_schema()` | Crea un schema |
| `drop_schema()` | Elimina un schema |
| `table_exists()` | Verifica si existe una tabla |
| `create_table()` | Crea una tabla |
| `drop_table()` | Elimina una tabla |
| `truncate_table()` | Trunca una tabla |
| `execute_ddl()` | Ejecuta DDL personalizado |
| `create_index()` | Crea un índice |
| `drop_index()` | Elimina un índice |

### Funciones DCL (19 funciones)

| Función | Descripción |
|---------|-------------|
| `role_exists()` | Verifica si existe un rol |
| `create_role()` | Crea un rol |
| `create_user()` | Crea un usuario |
| `drop_role()` | Elimina un rol |
| `drop_user()` | Elimina un usuario |
| `alter_role_password()` | Cambia contraseña |
| `grant_database_privileges()` | Otorga permisos en BD |
| `revoke_database_privileges()` | Revoca permisos en BD |
| `grant_schema_privileges()` | Otorga permisos en schema |
| `revoke_schema_privileges()` | Revoca permisos en schema |
| `grant_table_privileges()` | Otorga permisos en tabla |
| `revoke_table_privileges()` | Revoca permisos en tabla |
| `grant_all_tables_in_schema()` | Otorga permisos en todas las tablas |
| `grant_role_to_user()` | Asigna rol a usuario |
| `revoke_role_from_user()` | Revoca rol de usuario |
| `get_role_privileges()` | Obtiene privilegios de rol |
| `get_user_roles()` | Obtiene roles de usuario |
| `create_readonly_user()` | Crea usuario de solo lectura |
| `create_readwrite_user()` | Crea usuario con permisos completos |
| `get_active_connections()` | Obtiene conexiones activas |
| `get_connection_count()` | Cuenta conexiones |
| `terminate_connection()` | Termina una conexión |
| `terminate_all_connections()` | Termina todas las conexiones |

---

## Mejores Prácticas

### 1. Usar parámetros en queries

**✅ CORRECTO:**
```python
select('productos', where='precio < %s', where_params=(100,))
```

**❌ INCORRECTO (vulnerable a inyección SQL):**
```python
precio = 100
select('productos', where=f'precio < {precio}')
```

### 2. Gestión de transacciones

Para operaciones complejas, usar conexión directa:

```python
conn = get_postgres_connection()
cursor = conn.cursor()

try:
    cursor.execute("UPDATE cuentas SET saldo = saldo - %s WHERE id = %s", (100, 1))
    cursor.execute("UPDATE cuentas SET saldo = saldo + %s WHERE id = %s", (100, 2))
    conn.commit()
except:
    conn.rollback()
    raise
finally:
    cursor.close()
    conn.close()
```

### 3. Usar schemas para organizar

```python
# Crear schemas por módulo
create_schema('ventas')
create_schema('inventario')
create_schema('contabilidad')

# Usar schema en operaciones
select('productos', schema='inventario')
insert('facturas', {...}, schema='ventas')
```

### 4. Índices para mejorar rendimiento

```python
# Índice único para búsquedas frecuentes
create_index('idx_productos_codigo', 'productos', 'codigo', unique=True)

# Índice compuesto para consultas complejas
create_index('idx_ventas_fecha_cliente', 'ventas', ['fecha', 'cliente_id'])
```

### 5. Usar UPSERT en lugar de verificar + insertar/actualizar

**✅ CORRECTO:**
```python
upsert(
    'config',
    {'clave': 'version', 'valor': '1.2.0'},
    conflict_columns=['clave'],
    update_columns=['valor']
)
```

**❌ INCORRECTO (menos eficiente):**
```python
if exists('config', 'clave = %s', ('version',)):
    update('config', {'valor': '1.2.0'}, where='clave = %s', where_params=('version',))
else:
    insert('config', {'clave': 'version', 'valor': '1.2.0'})
```

---

**Versión:** 1.0.0
**Compatible con:** PostgreSQL 10+
**Dependencias:** psycopg2 >= 2.9
