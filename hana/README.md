## Resumen de lo Creado para SAP HANA

> ⚠️ **MÓDULO GENÉRICO**: Este módulo NO tiene valores por defecto hardcodeados. El usuario debe proporcionar TODAS las variables de conexión en el archivo `.env`. Ver [CONFIG.md](../README.md#-configuración) para más detalles.

He creado un módulo completo para SAP HANA similar al de MSSQL, con las siguientes características:

### 📦 Estructura del Módulo

```
hana/
├── __init__.py              # Exporta todas las funciones (39 funciones)
├── hana_dml.py              # Data Manipulation Language (13 funciones)
├── hana_ddl.py              # Data Definition Language (10 funciones)
├── hana_dcl.py              # Data Control Language (16 funciones)
└── README.md                # Documentación completa
```

### 🔧 Funciones Disponibles

#### DML - Data Manipulation Language (13 funciones)
- `get_hana_connection()` - Conexión a SAP HANA
- `insert()` - Insertar registro
- `insert_many()` - Inserción masiva por lotes
- `select()` - Consultar registros
- `select_one()` - Consultar un registro
- `update()` - Actualizar registros
- `delete()` - Eliminar registros
- `exists()` - Verificar existencia
- `count()` - Contar registros
- `upsert()` - Insertar o actualizar
- `truncate()` - Vaciar tabla
- `execute_query()` - Query personalizada
- `get_table_columns()` - Información de columnas

#### DDL - Data Definition Language (10 funciones)
- `schema_exists()` - Verificar si existe schema
- `get_schemas()` - Listar schemas con filtros personalizables
- `table_exists()` - Verificar si existe tabla
- `create_table()` - Crear tabla (ROW o COLUMN)
- `drop_table()` - Eliminar tabla
- `truncate_table()` - Vaciar tabla
- `execute_ddl()` - DDL personalizado
- `create_index()` - Crear índice
- `drop_index()` - Eliminar índice
- `get_table_info()` - Obtener información de tabla

#### DCL - Data Control Language (16 funciones)
**Usuarios:**
- `user_exists()` - Verificar usuario
- `create_user()` - Crear usuario
- `drop_user()` - Eliminar usuario

**Permisos:**
- `grant_permission()` - Otorgar permiso
- `revoke_permission()` - Revocar permiso
- `get_user_permissions()` - Consultar permisos

**Roles:**
- `role_exists()` - Verificar rol
- `create_role()` - Crear rol
- `drop_role()` - Eliminar rol
- `grant_role()` - Asignar rol a usuario
- `revoke_role()` - Revocar rol de usuario
- `get_user_roles()` - Consultar roles de usuario

**Conexiones:**
- `get_active_connections()` - Listar conexiones activas
- `get_connection_count()` - Contar conexiones

**Utilidades:**
- `create_readonly_user()` - Usuario de solo lectura
- `create_readwrite_user()` - Usuario de lectura/escritura

### 💡 Ejemplos de Uso

#### Ejemplo 1: Conexión y Consulta Simple
```python
from hana import *

# Conectar a un schema específico
conn = get_hana_connection(schema='SBODEMOUY')

# Consultar artículos
articulos = select(
    'OITM',
    columns=['ItemCode', 'ItemName', 'OnHand'],
    where='OnHand > ?',
    where_params=(0,),
    schema='SBODEMOUY'
)

for art in articulos:
    print(f"{art[0]}: {art[1]} (Stock: {art[2]})")
```

#### Ejemplo 2: Inserción de Datos
```python
from hana import *

# Insertar un registro
insert('MI_TABLA', {
    'CODIGO': 'P001',
    'NOMBRE': 'Producto 1',
    'PRECIO': 100.50
}, schema='MI_SCHEMA')

# Inserción masiva
datos = [
    ('P002', 'Producto 2', 200.00),
    ('P003', 'Producto 3', 300.00),
]

insert_many(
    'MI_TABLA',
    ['CODIGO', 'NOMBRE', 'PRECIO'],
    datos,
    schema='MI_SCHEMA',
    batch_size=1000
)
```

#### Ejemplo 3: Crear Tabla Column Store
```python
from hana import *

# Crear tabla tipo COLUMN (optimizada para analítica)
create_table(
    'VENTAS_ANALYTICS',
    {
        'ID': 'INTEGER',
        'FECHA': 'DATE',
        'CLIENTE': 'NVARCHAR(100)',
        'MONTO': 'DECIMAL(18,2)',
        'PRODUCTO': 'NVARCHAR(50)'
    },
    primary_key='ID',
    table_type='COLUMN',  # COLUMN para analítica, ROW para transaccional
    schema='MI_SCHEMA'
)
```

#### Ejemplo 4: Gestión de Usuarios y Permisos
```python
from hana import *

# Crear usuario de solo lectura
result = create_readonly_user(
    'APP_READONLY',
    'SecurePass123!',
    schema='SBODEMOUY'
)

# Crear usuario con permisos completos
result = create_readwrite_user(
    'APP_USER',
    'SecurePass123!',
    schema='SBODEMOUY'
)

# Ver permisos de un usuario
permisos = get_user_permissions('APP_USER')
for p in permisos:
    print(f"{p['object']}: {p['privilege']}")
```

#### Ejemplo 5: Monitoreo de Conexiones
```python
from hana import *

# Ver todas las conexiones activas
conexiones = get_active_connections()
for conn in conexiones:
    print(f"Connection ID: {conn['connection_id']}")
    print(f"  Usuario: {conn['user_name']}")
    print(f"  Host: {conn['client_host']}")
    print(f"  IP: {conn['client_ip']}")
    print(f"  Schema: {conn['current_schema']}")
    print(f"  Tiempo inactivo: {conn['idle_time']}")
    print()

# Contar conexiones por usuario
count = get_connection_count('B1ADMIN')
print(f"Conexiones de B1ADMIN: {count}")
```

#### Ejemplo 6: UPSERT (Insert or Update)
```python
from hana import *

# Insertar o actualizar según exista
rowcount, operation = upsert(
    'PRODUCTOS',
    {
        'CODIGO': 'P001',
        'NOMBRE': 'Producto Actualizado',
        'PRECIO': 150.00
    },
    key_columns=['CODIGO'],
    schema='MI_SCHEMA'
)

print(f"Operación: {operation} ({rowcount} fila(s))")
```

### 🔑 Configuración

⚠️ **El módulo es completamente genérico y NO tiene valores por defecto**.

El usuario DEBE configurar las siguientes variables de entorno en el archivo `.env`:

```env
# SAP HANA (REQUERIDO - Sin valores por defecto)
SAP_HANA_HOST=tu_servidor_hana
SAP_HANA_PORT=30015
SAP_HANA_USER=tu_usuario
SAP_HANA_PASSWORD=tu_password
```

**Nota**: Si alguna variable no está configurada, el módulo fallará al intentar conectarse. Ver [CONFIG.md](../README.md#-configuración) para documentación completa de configuración.

### 📊 Características Específicas de SAP HANA

1. **Table Types**:
   - `ROW` - Optimizada para transacciones (OLTP)
   - `COLUMN` - Optimizada para analítica (OLAP)

2. **Schemas**:
   - En SAP HANA, los schemas son fundamentales
   - Siempre especificar el schema al trabajar con objetos

3. **Conexiones**:
   - SAP HANA es in-memory
   - Las conexiones se gestionan de forma diferente a SQL Server

4. **Permisos**:
   - Permisos a nivel de schema, tabla y objeto
   - Sistema de roles integrado

### ⚠️ Advertencias Importantes

1. **NO ejecutar pruebas en producción**
   - El servidor SAP HANA configurado es de producción
   - No ejecutar tests automáticos sin autorización

2. **Operaciones DDL**
   - Las operaciones CREATE, DROP, ALTER son irreversibles
   - Usar siempre `if_exists` e `if_not_exists`

3. **Gestión de Usuarios**
   - Solo administradores deben crear/eliminar usuarios
   - Los cambios de permisos afectan el acceso a datos sensibles

### 📚 Diferencias con el Módulo MSSQL

| Característica | MSSQL | SAP HANA |
|---|---|---|
| Cliente | pyodbc | hdbcli |
| Tipos de tabla | Una sola | ROW y COLUMN |
| Schemas | Opcional | Fundamental |
| Vista de conexiones | sys.dm_exec_sessions | SYS.M_CONNECTIONS |
| Vista de usuarios | sys.users | SYS.USERS |
| Sintaxis LIMIT | TOP | LIMIT |

### 🎯 Uso Recomendado

```python
# Importar el módulo completo
from hana import *

# O importar funciones específicas
from hana import select, insert, get_active_connections

# Siempre especificar el schema cuando trabajes con SAP B1
schema = 'SBODEMOUY'  # Schema de tu empresa SAP B1

# Ejemplo: Consultar socios de negocio
socios = select(
    'OCRD',
    columns=['CardCode', 'CardName', 'CardType'],
    where='CardType = ?',
    where_params=('C',),  # C = Cliente, S = Proveedor
    schema=schema
)
```

### 📖 Documentación Adicional

Para más información sobre SAP HANA:
- [SAP HANA SQL Reference](https://help.sap.com/docs/HANA_SERVICE_CF/7c78579ce9b14a669c1f3295b0d8ca16/20a61c3975191014ad6aa2d96cdb0e3f.html)
- [SAP HANA Python Client (hdbcli)](https://help.sap.com/docs/SAP_HANA_CLIENT/f1b440ded6144a54ada97ff95dac7adf/39eca89d94ca464ca52385ad50fc7dea.html)

---

**Versión:** 1.0.0
**Última actualización:** 2026-01-23
**Compatible con:** SAP HANA 2.0+, Python 3.11+
