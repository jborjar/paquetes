# Módulo MSSQL - Documentación Completa

Biblioteca completa para operaciones con SQL Server que sigue el estándar SQL dividiendo las funciones en tres categorías principales: DML, DDL y DCL.

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

El módulo MSSQL proporciona una interfaz Python de alto nivel para interactuar con SQL Server, organizando las operaciones según el estándar SQL:

- **DML (Data Manipulation Language)**: Operaciones para manipular datos (INSERT, SELECT, UPDATE, DELETE)
- **DDL (Data Definition Language)**: Operaciones para definir estructuras (CREATE, DROP, ALTER)
- **DCL (Data Control Language)**: Operaciones para control de acceso (GRANT, REVOKE, usuarios, roles)

### Características principales

- Interfaz simplificada basada en pyodbc
- Manejo automático de conexiones
- Soporte para operaciones por lotes
- Funciones parametrizadas para prevenir inyección SQL
- Gestión completa de usuarios, roles y permisos
- Operaciones UPSERT (INSERT or UPDATE)

---

## Instalación y Configuración

### Requisitos

```bash
pip install pyodbc
```

### Configuración de variables de entorno

⚠️ **El módulo es completamente genérico y NO tiene valores por defecto**.

El usuario DEBE configurar las siguientes variables en el archivo `.env`:

```env
# Microsoft SQL Server (REQUERIDO - Sin valores por defecto)
MSSQL_HOST=tu_servidor
MSSQL_PORT=1433
MSSQL_USER=tu_usuario
MSSQL_PASSWORD=tu_password
MSSQL_DATABASE=tu_base_datos
```

**Nota**: Si alguna variable no está configurada, el módulo fallará al intentar conectarse. Ver [CONFIG.md](../README.md#-configuración) para documentación completa de configuración.

### Importación del módulo

```python
# Importar todas las funciones
from mssql import *

# O importar funciones específicas
from mssql import select, insert, create_table, grant_permission
```

---

## Estructura del Módulo

```
mssql/
├── __init__.py           # Exporta todas las funciones públicas
├── mssql_dml.py          # Funciones DML (manipulación de datos)
├── mssql_ddl.py          # Funciones DDL (definición de estructura)
├── mssql_dcl.py          # Funciones DCL (control de acceso)
└── test_mssql.py         # Suite de pruebas
```

---

## DML - Data Manipulation Language

Funciones para manipular datos en tablas existentes.

### Conexión a la base de datos

#### `get_mssql_connection(database=None)`

Obtiene una conexión activa a SQL Server.

**Parámetros:**
- `database` (str, opcional): Nombre de la base de datos. Si es None, usa la configurada en settings.

**Retorna:** Objeto `pyodbc.Connection`

**Ejemplo:**
```python
conn = get_mssql_connection()
conn = get_mssql_connection(database='otra_bd')
```

---

### Inserción de datos

#### `insert(table, data, database=None)`

Inserta un registro en una tabla.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `data` (dict): Diccionario con columnas y valores `{columna: valor}`
- `database` (str, opcional): Base de datos opcional

**Retorna:** Número de filas insertadas (normalmente 1)

**Ejemplo:**
```python
insert('SAP_EMPRESAS', {
    'Instancia': 'EMPRESA01',
    'SL': 1,
    'Prueba': 0,
    'PrintHeadr': 'Empresa 01'
})
```

#### `insert_many(table, columns, values_list, database=None, batch_size=1000)`

Inserta múltiples registros por lotes (más eficiente para grandes volúmenes).

**Parámetros:**
- `table` (str): Nombre de la tabla
- `columns` (list): Lista de nombres de columnas
- `values_list` (list): Lista de tuplas con valores
- `database` (str, opcional): Base de datos opcional
- `batch_size` (int): Tamaño del lote (default: 1000)

**Retorna:** Total de filas insertadas

**Ejemplo:**
```python
insert_many(
    'SAP_PROVEEDORES',
    ['Instancia', 'CardCode', 'CardName'],
    [
        ('EMPRESA01', 'P001', 'Proveedor 1'),
        ('EMPRESA01', 'P002', 'Proveedor 2'),
        ('EMPRESA01', 'P003', 'Proveedor 3'),
    ]
)
```

---

### Consulta de datos

#### `select(table, columns=None, where=None, where_params=None, order_by=None, limit=None, database=None)`

Consulta registros de una tabla.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `columns` (list, opcional): Lista de columnas a seleccionar (None = todas)
- `where` (str, opcional): Cláusula WHERE (sin la palabra WHERE)
- `where_params` (tuple, opcional): Parámetros para la cláusula WHERE
- `order_by` (str, opcional): Cláusula ORDER BY (sin las palabras ORDER BY)
- `limit` (int, opcional): Número máximo de registros (TOP en SQL Server)
- `database` (str, opcional): Base de datos opcional

**Retorna:** Lista de `pyodbc.Row`

**Ejemplos:**
```python
# Seleccionar todo
empresas = select('SAP_EMPRESAS')

# Con filtros
empresas_activas = select(
    'SAP_EMPRESAS',
    columns=['Instancia', 'PrintHeadr'],
    where='SL = ? AND Prueba = ?',
    where_params=(1, 0),
    order_by='Instancia'
)

# Con límite
top_10 = select('SAP_EMPRESAS', limit=10)
```

#### `select_one(table, columns=None, where=None, where_params=None, database=None)`

Consulta un solo registro de una tabla.

**Parámetros:** Similares a `select()`

**Retorna:** Primera fila encontrada (`pyodbc.Row`) o `None`

**Ejemplo:**
```python
empresa = select_one(
    'SAP_EMPRESAS',
    where='Instancia = ?',
    where_params=('EMPRESA01',)
)
```

---

### Actualización de datos

#### `update(table, data, where, where_params, database=None)`

Actualiza registros en una tabla.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `data` (dict): Diccionario con columnas y valores a actualizar
- `where` (str): Cláusula WHERE (sin la palabra WHERE)
- `where_params` (tuple): Parámetros para la cláusula WHERE
- `database` (str, opcional): Base de datos opcional

**Retorna:** Número de filas actualizadas

**Ejemplo:**
```python
filas_actualizadas = update(
    'SAP_EMPRESAS',
    {'SL': 1, 'PrintHeadr': 'Nueva Empresa'},
    where='Instancia = ?',
    where_params=('EMPRESA01',)
)
```

---

### Eliminación de datos

#### `delete(table, where, where_params, database=None)`

Elimina registros de una tabla.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `where` (str): Cláusula WHERE (sin la palabra WHERE)
- `where_params` (tuple): Parámetros para la cláusula WHERE
- `database` (str, opcional): Base de datos opcional

**Retorna:** Número de filas eliminadas

**Ejemplo:**
```python
filas_eliminadas = delete(
    'SAP_EMPRESAS',
    where='Instancia = ?',
    where_params=('EMPRESA01',)
)
```

#### `truncate(table, database=None)`

Vacía completamente una tabla (más rápido que DELETE).

**ADVERTENCIA:** Esta operación no se puede deshacer.

**Ejemplo:**
```python
truncate('SAP_PROV_TEMP')
```

---

### Operaciones de verificación

#### `exists(table, where, where_params, database=None)`

Verifica si existe al menos un registro que cumpla la condición.

**Retorna:** `True` o `False`

**Ejemplo:**
```python
if exists('SAP_EMPRESAS', 'Instancia = ?', ('EMPRESA01',)):
    print('La empresa existe')
```

#### `count(table, where=None, where_params=None, database=None)`

Cuenta registros en una tabla.

**Retorna:** Número de registros (int)

**Ejemplo:**
```python
# Contar todos
total = count('SAP_EMPRESAS')

# Con filtro
activos = count('SAP_EMPRESAS', where='SL = ?', where_params=(1,))
```

---

### Operaciones avanzadas

#### `upsert(table, data, key_columns, database=None)`

Inserta o actualiza un registro (UPSERT/MERGE).

**Parámetros:**
- `table` (str): Nombre de la tabla
- `data` (dict): Diccionario con todas las columnas y valores
- `key_columns` (list): Lista de columnas que forman la llave primaria
- `database` (str, opcional): Base de datos opcional

**Retorna:** Tupla `(rowcount, operation)` donde operation es 'inserted' o 'updated'

**Ejemplo:**
```python
filas, operacion = upsert(
    'SAP_EMPRESAS',
    {
        'Instancia': 'EMPRESA01',
        'SL': 1,
        'Prueba': 0,
        'PrintHeadr': 'Empresa 01'
    },
    key_columns=['Instancia']
)
print(f"{filas} fila(s) {operacion}")
```

#### `execute_query(query, params=None, database=None, fetch=True)`

Ejecuta una query SQL personalizada.

**Parámetros:**
- `query` (str): Query SQL completa
- `params` (tuple, opcional): Parámetros para la query
- `database` (str, opcional): Base de datos opcional
- `fetch` (bool): Si True retorna resultados, si False retorna rowcount

**Retorna:** Lista de filas o número de filas afectadas

**Ejemplo:**
```python
# SELECT personalizado
resultados = execute_query(
    "SELECT * FROM SAP_EMPRESAS WHERE SL = ? AND Prueba = ?",
    params=(1, 0)
)

# UPDATE personalizado
filas = execute_query(
    "UPDATE SAP_EMPRESAS SET SL = 1 WHERE Instancia LIKE ?",
    params=('EMP%',),
    fetch=False
)
```

#### `get_table_columns(table, database=None)`

Obtiene información de las columnas de una tabla.

**Retorna:** Lista de diccionarios con información de cada columna

**Ejemplo:**
```python
columnas = get_table_columns('SAP_EMPRESAS')
for col in columnas:
    print(f"{col['name']}: {col['type']} ({col['max_length']})")
```

---

## DDL - Data Definition Language

Funciones para crear y modificar la estructura de bases de datos y tablas.

**ADVERTENCIA:** Las operaciones DDL modifican la estructura de la base de datos y pueden ser irreversibles. Usar con precaución.

### Gestión de bases de datos

#### `database_exists(database)`

Verifica si una base de datos existe.

**Retorna:** `True` o `False`

**Ejemplo:**
```python
if database_exists('API_MCP'):
    print('La base de datos existe')
```

#### `create_database(database, if_not_exists=True)`

Crea una base de datos en SQL Server.

**Parámetros:**
- `database` (str): Nombre de la base de datos
- `if_not_exists` (bool): Si True, solo crea si no existe (default: True)

**Retorna:** `True` si se creó, `False` si ya existía

**Ejemplo:**
```python
create_database('MI_BASE_DATOS')
```

#### `drop_database(database, if_exists=True, force=False)`

Elimina una base de datos de SQL Server.

**ADVERTENCIA:** Esta operación es IRREVERSIBLE.

**Parámetros:**
- `database` (str): Nombre de la base de datos
- `if_exists` (bool): Si True, no genera error si no existe (default: True)
- `force` (bool): Si True, cierra todas las conexiones activas antes de eliminar (default: False)

**Retorna:** `True` si se eliminó, `False` si no existía

**Ejemplo:**
```python
drop_database('MI_BASE_DATOS', force=True)
```

#### `recreate_database(database)`

Elimina y recrea una base de datos desde cero.

**ADVERTENCIA:** Esta operación elimina TODOS los datos de la base de datos.

**Ejemplo:**
```python
recreate_database('API_MCP')
```

---

### Gestión de tablas

#### `table_exists(table, database=None)`

Verifica si una tabla existe en la base de datos.

**Retorna:** `True` o `False`

**Ejemplo:**
```python
if table_exists('SAP_EMPRESAS'):
    print('La tabla existe')
```

#### `create_table(table, columns, primary_key=None, if_not_exists=True, database=None)`

Crea una tabla en SQL Server.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `columns` (dict): Diccionario `{nombre_columna: definición_tipo}`
- `primary_key` (list/str, opcional): Columna(s) que forman la llave primaria
- `if_not_exists` (bool): Si True, solo crea si no existe (default: True)
- `database` (str, opcional): Base de datos opcional

**Retorna:** `True` si se creó, `False` si ya existía

**Ejemplo:**
```python
create_table(
    'MI_TABLA',
    {
        'id': 'INT IDENTITY(1,1)',
        'nombre': 'NVARCHAR(100) NOT NULL',
        'email': 'NVARCHAR(100)',
        'activo': 'BIT DEFAULT 1',
        'fecha_creacion': 'DATETIME DEFAULT GETDATE()'
    },
    primary_key='id'
)

# Llave primaria compuesta
create_table(
    'MI_TABLA_COMPUESTA',
    {
        'empresa': 'NVARCHAR(50)',
        'codigo': 'NVARCHAR(50)',
        'nombre': 'NVARCHAR(100)'
    },
    primary_key=['empresa', 'codigo']
)
```

#### `drop_table(table, if_exists=True, database=None)`

Elimina una tabla de SQL Server.

**ADVERTENCIA:** Esta operación es IRREVERSIBLE.

**Ejemplo:**
```python
drop_table('MI_TABLA')
```

#### `truncate_table(table, database=None)`

Vacía completamente una tabla (TRUNCATE).

**ADVERTENCIA:** Esta operación elimina TODOS los registros y no se puede deshacer.

**Ejemplo:**
```python
truncate_table('SAP_PROV_TEMP')
```

---

### Gestión de índices

#### `create_index(table, index_name, columns, unique=False, if_not_exists=True, database=None)`

Crea un índice en una tabla.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `index_name` (str): Nombre del índice
- `columns` (list/str): Columna(s) del índice
- `unique` (bool): Si True, crea índice único (default: False)
- `if_not_exists` (bool): Si True, solo crea si no existe (default: True)
- `database` (str, opcional): Base de datos opcional

**Retorna:** `True` si se creó, `False` si ya existía

**Ejemplo:**
```python
# Índice simple
create_index('SAP_PROVEEDORES', 'idx_cardcode', 'CardCode')

# Índice compuesto único
create_index(
    'SAP_PROVEEDORES',
    'idx_inst_card',
    ['Instancia', 'CardCode'],
    unique=True
)
```

#### `drop_index(table, index_name, if_exists=True, database=None)`

Elimina un índice de una tabla.

**Ejemplo:**
```python
drop_index('SAP_PROVEEDORES', 'idx_cardcode')
```

---

### Operaciones DDL personalizadas

#### `execute_ddl(ddl_statement, database=None)`

Ejecuta una sentencia DDL (CREATE, ALTER, DROP, etc.).

**Ejemplo:**
```python
# Crear tabla con DDL personalizado
execute_ddl('''
    CREATE TABLE MiTabla (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(100) NOT NULL,
        fecha DATETIME DEFAULT GETDATE()
    )
''')

# Alterar tabla
execute_ddl('ALTER TABLE MiTabla ADD email NVARCHAR(100)')

# Crear vista
execute_ddl('''
    CREATE VIEW vw_Empresas_Activas AS
    SELECT * FROM SAP_EMPRESAS WHERE SL = 1
''')
```

---

## DCL - Data Control Language

Funciones para control de acceso, usuarios, roles y permisos.

**ADVERTENCIA:** Las operaciones DCL modifican permisos y seguridad. Solo deben ser ejecutadas por administradores de base de datos.

### Gestión de Logins (nivel servidor)

#### `login_exists(login_name)`

Verifica si un login existe en el servidor.

**Retorna:** `True` o `False`

**Ejemplo:**
```python
if login_exists('mi_usuario'):
    print('El login existe')
```

#### `create_login(login_name, password, default_database='master', if_not_exists=True)`

Crea un login (autenticación SQL Server) en el servidor.

**Parámetros:**
- `login_name` (str): Nombre del login
- `password` (str): Contraseña del login
- `default_database` (str): Base de datos por defecto (default: 'master')
- `if_not_exists` (bool): Si True, solo crea si no existe (default: True)

**Retorna:** `True` si se creó, `False` si ya existía

**Ejemplo:**
```python
create_login('app_user', 'P@ssw0rd!123', default_database='API_MCP')
```

#### `drop_login(login_name, if_exists=True)`

Elimina un login del servidor SQL Server.

**Ejemplo:**
```python
drop_login('app_user')
```

---

### Gestión de Usuarios (nivel base de datos)

#### `user_exists(user_name, database=None)`

Verifica si un usuario existe en una base de datos.

**Retorna:** `True` o `False`

**Ejemplo:**
```python
if user_exists('app_user', database='API_MCP'):
    print('El usuario existe')
```

#### `create_user(user_name, login_name=None, default_schema='dbo', if_not_exists=True, database=None)`

Crea un usuario en una base de datos.

**Parámetros:**
- `user_name` (str): Nombre del usuario
- `login_name` (str, opcional): Nombre del login asociado (si None, usa user_name)
- `default_schema` (str): Schema por defecto (default: 'dbo')
- `if_not_exists` (bool): Si True, solo crea si no existe (default: True)
- `database` (str, opcional): Base de datos opcional

**Retorna:** `True` si se creó, `False` si ya existía

**Ejemplo:**
```python
create_user('app_user', login_name='app_user', database='API_MCP')
```

#### `drop_user(user_name, if_exists=True, database=None)`

Elimina un usuario de una base de datos.

**Ejemplo:**
```python
drop_user('app_user', database='API_MCP')
```

---

### Gestión de Permisos

#### `grant_permission(permission, object_name=None, user_name=None, database=None)`

Otorga un permiso a un usuario.

**Parámetros:**
- `permission` (str): Tipo de permiso (SELECT, INSERT, UPDATE, DELETE, EXECUTE, etc.)
- `object_name` (str, opcional): Nombre del objeto (tabla, vista, procedimiento). Si None, otorga a nivel BD
- `user_name` (str): Nombre del usuario que recibe el permiso
- `database` (str, opcional): Base de datos opcional

**Ejemplo:**
```python
# Permiso a nivel de tabla
grant_permission('SELECT', 'SAP_EMPRESAS', 'app_user')

# Permiso a nivel de base de datos
grant_permission('CREATE TABLE', user_name='app_user')
```

#### `revoke_permission(permission, object_name=None, user_name=None, database=None)`

Revoca un permiso de un usuario.

**Ejemplo:**
```python
revoke_permission('DELETE', 'SAP_EMPRESAS', 'app_user')
```

#### `deny_permission(permission, object_name=None, user_name=None, database=None)`

Deniega explícitamente un permiso a un usuario.

**NOTA:** DENY tiene prioridad sobre GRANT. Usar con precaución.

**Ejemplo:**
```python
deny_permission('DELETE', 'SAP_EMPRESAS', 'readonly_user')
```

#### `grant_table_permissions(table, user_name, permissions, database=None)`

Otorga múltiples permisos sobre una tabla a un usuario.

**Parámetros:**
- `table` (str): Nombre de la tabla
- `user_name` (str): Nombre del usuario
- `permissions` (list): Lista de permisos
- `database` (str, opcional): Base de datos opcional

**Ejemplo:**
```python
grant_table_permissions(
    'SAP_EMPRESAS',
    'app_user',
    ['SELECT', 'INSERT', 'UPDATE']
)
```

#### `get_user_permissions(user_name, database=None)`

Obtiene los permisos de un usuario en la base de datos.

**Retorna:** Lista de diccionarios con información de permisos

**Ejemplo:**
```python
permisos = get_user_permissions('app_user')
for p in permisos:
    print(f"{p['object']}: {p['permission']} ({p['state']})")
```

---

### Gestión de Roles

#### `role_exists(role_name, database=None)`

Verifica si un rol existe en una base de datos.

**Retorna:** `True` o `False`

**Ejemplo:**
```python
if role_exists('app_readonly'):
    print('El rol existe')
```

#### `create_role(role_name, if_not_exists=True, database=None)`

Crea un rol en una base de datos.

**Ejemplo:**
```python
create_role('app_readonly')
```

#### `drop_role(role_name, if_exists=True, database=None)`

Elimina un rol de una base de datos.

**Ejemplo:**
```python
drop_role('app_readonly')
```

#### `add_user_to_role(user_name, role_name, database=None)`

Agrega un usuario a un rol.

**Ejemplo:**
```python
add_user_to_role('app_user', 'db_datareader')
```

#### `remove_user_from_role(user_name, role_name, database=None)`

Remueve un usuario de un rol.

**Ejemplo:**
```python
remove_user_from_role('app_user', 'db_datareader')
```

#### `get_user_roles(user_name, database=None)`

Obtiene los roles de un usuario.

**Retorna:** Lista de nombres de roles

**Ejemplo:**
```python
roles = get_user_roles('app_user')
print(f"Roles: {', '.join(roles)}")
```

---

### Utilidades de Seguridad

#### `create_readonly_user(user_name, login_name=None, password=None, database=None)`

Crea un usuario con permisos de solo lectura (SELECT en todas las tablas).

**Parámetros:**
- `user_name` (str): Nombre del usuario
- `login_name` (str, opcional): Nombre del login (si None, usa user_name)
- `password` (str, opcional): Contraseña del login (requerida si el login no existe)
- `database` (str, opcional): Base de datos opcional

**Retorna:** Diccionario con el resultado de cada operación

**Ejemplo:**
```python
result = create_readonly_user('readonly_user', password='Pass123!')
print(result)
# {'login_created': True, 'user_created': True, 'role_assigned': True}
```

#### `create_readwrite_user(user_name, login_name=None, password=None, database=None)`

Crea un usuario con permisos de lectura y escritura.

**Ejemplo:**
```python
result = create_readwrite_user('app_user', password='Pass123!')
print(result)
# {'login_created': True, 'user_created': True, 'roles_assigned': True}
```

---

### Gestión de Conexiones Activas

#### `get_active_connections(database=None)`

Obtiene lista de conexiones activas a la base de datos.

**Parámetros:**
- `database` (str, opcional): Base de datos específica (si None, muestra todas las conexiones del servidor)

**Retorna:** Lista de diccionarios con información de cada conexión activa

**Ejemplo:**
```python
# Ver todas las conexiones
conexiones = get_active_connections()
for conn in conexiones:
    print(f"SPID: {conn['session_id']}, Usuario: {conn['login_name']}, DB: {conn['database_name']}")

# Ver conexiones de una base de datos específica
conexiones_api = get_active_connections(database='API_MCP')
for conn in conexiones_api:
    print(f"SPID: {conn['session_id']}")
    print(f"Usuario: {conn['login_name']}")
    print(f"Host: {conn['host_name']}")
    print(f"Programa: {conn['program_name']}")
    print(f"Estado: {conn['status']}")
    print(f"IP: {conn['client_net_address']}")
    print(f"Conectado desde: {conn['login_time']}")
    print("---")
```

#### `get_connection_count(database=None)`

Obtiene el número de conexiones activas.

**Parámetros:**
- `database` (str, opcional): Base de datos específica (si None, cuenta todas las conexiones)

**Retorna:** Número de conexiones activas (int)

**Ejemplo:**
```python
# Contar todas las conexiones
total = get_connection_count()
print(f"Conexiones totales: {total}")

# Contar conexiones a una base de datos específica
count = get_connection_count('API_MCP')
print(f"Conexiones a API_MCP: {count}")
```

#### `kill_connection(session_id)`

Cierra (mata) una conexión específica por su session_id.

**ADVERTENCIA:** Esta operación termina abruptamente la conexión. Usar con precaución.

**Parámetros:**
- `session_id` (int): ID de la sesión a cerrar (SPID)

**Retorna:** `True` si se cerró la conexión exitosamente

**Ejemplo:**
```python
# Primero listar las conexiones para obtener el session_id
conexiones = get_active_connections(database='API_MCP')
for conn in conexiones:
    if conn['login_name'] == 'usuario_a_desconectar':
        print(f"Cerrando sesión {conn['session_id']}")
        kill_connection(conn['session_id'])
```

#### `kill_all_connections(database, exclude_current=True)`

Cierra todas las conexiones activas a una base de datos.

**ADVERTENCIA:** Esta operación termina abruptamente todas las conexiones. Útil para mantenimiento o antes de eliminar una base de datos.

**Parámetros:**
- `database` (str): Nombre de la base de datos
- `exclude_current` (bool): Si True, no cierra la conexión actual (default: True)

**Retorna:** Número de conexiones cerradas (int)

**Ejemplo:**
```python
# Cerrar todas las conexiones excepto la actual
count = kill_all_connections('API_MCP')
print(f"Se cerraron {count} conexiones")

# Cerrar absolutamente todas las conexiones (incluyendo la actual)
count = kill_all_connections('API_MCP', exclude_current=False)

# Uso típico: antes de eliminar una base de datos
kill_all_connections('BD_ANTIGUA', exclude_current=True)
drop_database('BD_ANTIGUA', force=True)
```

---

## Ejemplos de Uso

### Ejemplo 1: CRUD Completo

```python
from mssql import *

# 1. Crear tabla
create_table(
    'Empleados',
    {
        'id': 'INT IDENTITY(1,1)',
        'nombre': 'NVARCHAR(100) NOT NULL',
        'email': 'NVARCHAR(100)',
        'salario': 'DECIMAL(10,2)',
        'activo': 'BIT DEFAULT 1'
    },
    primary_key='id'
)

# 2. Insertar datos
insert('Empleados', {
    'nombre': 'Juan Pérez',
    'email': 'juan@example.com',
    'salario': 50000.00,
    'activo': 1
})

# 3. Leer datos
empleados = select('Empleados', where='activo = ?', where_params=(1,))
for emp in empleados:
    print(f"{emp.nombre}: {emp.email}")

# 4. Actualizar datos
update(
    'Empleados',
    {'salario': 55000.00},
    where='nombre = ?',
    where_params=('Juan Pérez',)
)

# 5. Eliminar datos
delete('Empleados', where='activo = ?', where_params=(0,))
```

### Ejemplo 2: Inserción Masiva

```python
from mssql import *

# Preparar datos
empleados = [
    ('Juan Pérez', 'juan@example.com', 50000),
    ('María García', 'maria@example.com', 55000),
    ('Carlos López', 'carlos@example.com', 60000),
    # ... más empleados
]

# Insertar por lotes (más eficiente)
insert_many(
    'Empleados',
    ['nombre', 'email', 'salario'],
    empleados,
    batch_size=1000
)
```

### Ejemplo 3: Operación UPSERT

```python
from mssql import *

# Inserta si no existe, actualiza si existe
filas, operacion = upsert(
    'SAP_EMPRESAS',
    {
        'Instancia': 'EMPRESA01',
        'SL': 1,
        'Prueba': 0,
        'PrintHeadr': 'Empresa Actualizada'
    },
    key_columns=['Instancia']
)

print(f"Operación: {operacion} ({filas} fila(s))")
```

### Ejemplo 4: Gestión de Usuarios y Permisos

```python
from mssql import *

# 1. Crear login y usuario de solo lectura
result = create_readonly_user(
    'app_readonly',
    password='SecurePass123!',
    database='API_MCP'
)

# 2. Crear usuario con permisos personalizados
create_login('app_custom', 'CustomPass123!', default_database='API_MCP')
create_user('app_custom', database='API_MCP')

# 3. Otorgar permisos específicos
grant_table_permissions(
    'SAP_EMPRESAS',
    'app_custom',
    ['SELECT', 'INSERT'],
    database='API_MCP'
)

# 4. Verificar permisos
permisos = get_user_permissions('app_custom', database='API_MCP')
for p in permisos:
    print(f"{p['object']}: {p['permission']} ({p['state']})")
```

### Ejemplo 5: Gestión de Base de Datos Completa

```python
from mssql import *

# 1. Crear base de datos
create_database('MI_APLICACION')

# 2. Crear tablas
create_table(
    'Clientes',
    {
        'id': 'INT IDENTITY(1,1)',
        'nombre': 'NVARCHAR(100) NOT NULL',
        'email': 'NVARCHAR(100) UNIQUE'
    },
    primary_key='id',
    database='MI_APLICACION'
)

# 3. Crear índices
create_index(
    'Clientes',
    'idx_email',
    'email',
    unique=True,
    database='MI_APLICACION'
)

# 4. Insertar datos
insert('Clientes', {
    'nombre': 'Cliente 1',
    'email': 'cliente1@example.com'
}, database='MI_APLICACION')

# 5. Consultar datos
clientes = select('Clientes', database='MI_APLICACION')
```

### Ejemplo 6: Transacciones con Query Personalizada

```python
from mssql import *

# Ejecutar varias operaciones en una transacción
conn = get_mssql_connection()
cursor = conn.cursor()

try:
    # Operación 1
    cursor.execute("UPDATE Empleados SET salario = salario * 1.1 WHERE activo = 1")

    # Operación 2
    cursor.execute("INSERT INTO Auditoria (accion, fecha) VALUES (?, GETDATE())",
                   ('Aumento de salarios',))

    # Confirmar transacción
    conn.commit()
    print("Transacción completada exitosamente")

except Exception as e:
    # Revertir transacción en caso de error
    conn.rollback()
    print(f"Error: {e}")

finally:
    cursor.close()
    conn.close()
```

### Ejemplo 7: Gestión de Conexiones Activas

```python
from mssql import *

# 1. Ver todas las conexiones activas en el servidor
print("=== Todas las conexiones ===")
conexiones = get_active_connections()
for conn in conexiones:
    print(f"SPID: {conn['session_id']}, Usuario: {conn['login_name']}, "
          f"DB: {conn['database_name']}, Host: {conn['host_name']}")

# 2. Ver conexiones de una base de datos específica
print("\n=== Conexiones a API_MCP ===")
conexiones_api = get_active_connections(database='API_MCP')
for conn in conexiones_api:
    print(f"SPID {conn['session_id']}:")
    print(f"  Usuario: {conn['login_name']}")
    print(f"  Host: {conn['host_name']}")
    print(f"  Programa: {conn['program_name']}")
    print(f"  Estado: {conn['status']}")
    print(f"  IP: {conn['client_net_address']}")
    print(f"  Conectado desde: {conn['login_time']}")
    print()

# 3. Contar conexiones
total = get_connection_count()
api_count = get_connection_count('API_MCP')
print(f"\nConexiones totales: {total}")
print(f"Conexiones a API_MCP: {api_count}")

# 4. Cerrar una conexión específica
# (útil para desconectar un usuario problemático)
conexiones = get_active_connections(database='API_MCP')
for conn in conexiones:
    if conn['login_name'] == 'usuario_bloqueado':
        print(f"\nCerrando sesión {conn['session_id']} del usuario {conn['login_name']}")
        kill_connection(conn['session_id'])

# 5. Mantenimiento: Cerrar todas las conexiones antes de una operación
print("\n=== Preparando mantenimiento ===")
# Cerrar todas las conexiones a una BD (excepto la actual)
count = kill_all_connections('BD_MANTENIMIENTO')
print(f"Se cerraron {count} conexiones a BD_MANTENIMIENTO")

# Ahora se puede hacer el mantenimiento
recreate_database('BD_MANTENIMIENTO')

# 6. Monitoreo continuo de conexiones
def monitorear_conexiones(database, max_conexiones=50):
    """Monitorea y alerta si hay muchas conexiones"""
    count = get_connection_count(database)

    if count > max_conexiones:
        print(f"¡ALERTA! {count} conexiones activas (límite: {max_conexiones})")
        conexiones = get_active_connections(database)

        # Mostrar detalles de las conexiones
        usuarios = {}
        for conn in conexiones:
            usuario = conn['login_name']
            usuarios[usuario] = usuarios.get(usuario, 0) + 1

        print("Conexiones por usuario:")
        for usuario, cantidad in sorted(usuarios.items(), key=lambda x: x[1], reverse=True):
            print(f"  {usuario}: {cantidad}")
    else:
        print(f"OK: {count} conexiones activas")

monitorear_conexiones('API_MCP', max_conexiones=100)
```

---

## Referencia Rápida

### DML - Manipulación de Datos

| Función | Descripción |
|---------|-------------|
| `get_mssql_connection()` | Obtiene conexión a SQL Server |
| `insert()` | Inserta un registro |
| `insert_many()` | Inserta múltiples registros por lotes |
| `select()` | Consulta registros |
| `select_one()` | Consulta un solo registro |
| `update()` | Actualiza registros |
| `delete()` | Elimina registros |
| `exists()` | Verifica si existe un registro |
| `count()` | Cuenta registros |
| `upsert()` | Inserta o actualiza (MERGE) |
| `truncate()` | Vacía una tabla completamente |
| `execute_query()` | Ejecuta query SQL personalizada |
| `get_table_columns()` | Obtiene información de columnas |

### DDL - Definición de Estructura

| Función | Descripción |
|---------|-------------|
| `database_exists()` | Verifica si existe una base de datos |
| `create_database()` | Crea una base de datos |
| `drop_database()` | Elimina una base de datos |
| `recreate_database()` | Recrea una base de datos |
| `table_exists()` | Verifica si existe una tabla |
| `create_table()` | Crea una tabla |
| `drop_table()` | Elimina una tabla |
| `truncate_table()` | Vacía una tabla (TRUNCATE) |
| `create_index()` | Crea un índice |
| `drop_index()` | Elimina un índice |
| `execute_ddl()` | Ejecuta DDL personalizado |

### DCL - Control de Acceso

| Función | Descripción |
|---------|-------------|
| **Logins (servidor)** | |
| `login_exists()` | Verifica si existe un login |
| `create_login()` | Crea un login |
| `drop_login()` | Elimina un login |
| **Usuarios (base de datos)** | |
| `user_exists()` | Verifica si existe un usuario |
| `create_user()` | Crea un usuario |
| `drop_user()` | Elimina un usuario |
| **Permisos** | |
| `grant_permission()` | Otorga un permiso |
| `revoke_permission()` | Revoca un permiso |
| `deny_permission()` | Deniega un permiso |
| `grant_table_permissions()` | Otorga múltiples permisos en tabla |
| `get_user_permissions()` | Obtiene permisos de un usuario |
| **Roles** | |
| `role_exists()` | Verifica si existe un rol |
| `create_role()` | Crea un rol |
| `drop_role()` | Elimina un rol |
| `add_user_to_role()` | Agrega usuario a un rol |
| `remove_user_from_role()` | Remueve usuario de un rol |
| `get_user_roles()` | Obtiene roles de un usuario |
| **Utilidades** | |
| `create_readonly_user()` | Crea usuario de solo lectura |
| `create_readwrite_user()` | Crea usuario de lectura/escritura |
| **Gestión de conexiones** | |
| `get_active_connections()` | Lista conexiones activas |
| `get_connection_count()` | Cuenta conexiones activas |
| `kill_connection()` | Cierra una conexión específica |
| `kill_all_connections()` | Cierra todas las conexiones a una BD |

---

## Mejores Prácticas

### 1. Seguridad

```python
# BUENO: Usar parámetros (previene inyección SQL)
select('Usuarios', where='nombre = ?', where_params=(nombre_usuario,))

# MALO: Concatenar strings (vulnerable a inyección SQL)
# execute_query(f"SELECT * FROM Usuarios WHERE nombre = '{nombre_usuario}'")
```

### 2. Manejo de Conexiones

```python
# Para operaciones simples, usa las funciones wrapper (manejan conexión automáticamente)
empresas = select('SAP_EMPRESAS')

# Para operaciones complejas o transacciones, maneja la conexión manualmente
conn = get_mssql_connection()
try:
    cursor = conn.cursor()
    # ... operaciones múltiples ...
    conn.commit()
finally:
    cursor.close()
    conn.close()
```

### 3. Inserción Masiva

```python
# BUENO: Usar insert_many para grandes volúmenes
insert_many('Tabla', ['col1', 'col2'], datos_masivos, batch_size=1000)

# MALO: Múltiples insert individuales (muy lento)
# for fila in datos_masivos:
#     insert('Tabla', {'col1': fila[0], 'col2': fila[1]})
```

### 4. Verificación de Existencia

```python
# BUENO: Usar funciones de existencia
if table_exists('MiTabla'):
    print('La tabla existe')

# MALO: Try/except para verificar existencia
# try:
#     select('MiTabla', limit=1)
# except:
#     print('La tabla no existe')
```

### 5. Operaciones DDL

```python
# BUENO: Usar if_not_exists/if_exists
create_table('MiTabla', columnas, if_not_exists=True)
drop_table('MiTabla', if_exists=True)

# MALO: No verificar y manejar excepciones
# create_table('MiTabla', columnas)  # Error si ya existe
```

### 6. Gestión de Permisos

```python
# BUENO: Usar roles predefinidos cuando sea posible
add_user_to_role('usuario', 'db_datareader')

# BUENO: Usar funciones de utilidad para casos comunes
create_readonly_user('usuario_lectura', password='Pass123!')

# Para permisos personalizados, otorgar el mínimo necesario
grant_table_permissions('Tabla', 'usuario', ['SELECT', 'INSERT'])
```

### 7. Nombres de Objetos

```python
# BUENO: Usar nombres descriptivos
create_table('SAP_Proveedores', columnas)
create_index('SAP_Proveedores', 'idx_cardcode', 'CardCode')

# MALO: Nombres genéricos o confusos
# create_table('Tabla1', columnas)
# create_index('Tabla1', 'idx1', 'col1')
```

### 8. Documentación y Comentarios

```python
# Documenta operaciones importantes
# Crear tabla de proveedores con índice en CardCode para mejorar rendimiento
create_table('SAP_Proveedores', {
    'CardCode': 'NVARCHAR(50) NOT NULL',
    'CardName': 'NVARCHAR(100)',
    # ... más columnas
}, primary_key='CardCode')

create_index('SAP_Proveedores', 'idx_cardname', 'CardName')
```

### 9. Gestión de Conexiones

```python
# BUENO: Monitorear conexiones periódicamente
conexiones = get_active_connections(database='API_MCP')
if get_connection_count('API_MCP') > 100:
    print("Demasiadas conexiones activas")

# BUENO: Cerrar conexiones antes de operaciones de mantenimiento
kill_all_connections('BD_MANTENIMIENTO', exclude_current=True)
recreate_database('BD_MANTENIMIENTO')

# BUENO: Identificar y cerrar conexiones problemáticas
for conn in get_active_connections('API_MCP'):
    # Cerrar conexiones inactivas por más de 1 hora
    if conn['status'] == 'sleeping':
        kill_connection(conn['session_id'])

# MALO: No verificar conexiones activas antes de eliminar una BD
# drop_database('MI_BD')  # Puede fallar si hay conexiones activas
```

---

## Notas Adicionales

### Tipos de Datos Comunes en SQL Server

```python
# Tipos numéricos
'INT'                      # Entero
'BIGINT'                   # Entero largo
'DECIMAL(10,2)'            # Decimal (10 dígitos, 2 decimales)
'FLOAT'                    # Punto flotante

# Tipos de texto
'NVARCHAR(100)'            # Texto Unicode (longitud variable)
'NVARCHAR(MAX)'            # Texto Unicode (longitud máxima)
'NCHAR(10)'                # Texto Unicode (longitud fija)

# Tipos de fecha/hora
'DATE'                     # Solo fecha
'DATETIME'                 # Fecha y hora
'DATETIME2'                # Fecha y hora (más preciso)
'TIME'                     # Solo hora

# Otros tipos
'BIT'                      # Booleano (0 o 1)
'UNIQUEIDENTIFIER'         # GUID
'VARBINARY(MAX)'           # Datos binarios
```

### Roles Predefinidos en SQL Server

```python
# Roles a nivel de base de datos
'db_owner'          # Propietario de la base de datos (todos los permisos)
'db_datareader'     # Leer datos de todas las tablas
'db_datawriter'     # Escribir datos en todas las tablas
'db_ddladmin'       # Ejecutar comandos DDL (CREATE, ALTER, DROP)
'db_securityadmin'  # Gestionar permisos y roles
'db_backupoperator' # Hacer backups de la base de datos
'db_denydatareader' # Denegar lectura de datos
'db_denydatawriter' # Denegar escritura de datos
```

---

## Soporte y Contribuciones

Para reportar problemas o sugerir mejoras, por favor contacta al equipo de desarrollo.

### Requisitos del Sistema

- Python 3.11+
- pyodbc 5.0.1+
- SQL Server 2019+
- ODBC Driver 18 for SQL Server

---

**Versión:** 1.0.0
**Última actualización:** 2026-01-31
