# Pruebas de Paquetes

Este directorio contiene todas las pruebas y scripts de configuración para los módulos de paquetes.

## 📋 Contenido

```
tests/
├── README.md                       # Este archivo
│
├── auth/                           # Tests del módulo auth
│   ├── example_auth_fastapi.py
│   └── example_auth_flask.py
│
├── ldap/                           # Tests del módulo ldap
│   ├── test_ldap.py
│   ├── test_ldap_debug.py
│   ├── test_ldaps_*.py            # Variantes LDAPS
│   ├── example_ldap_*.py
│   ├── demo_ldaps_support.py
│   └── LDAPS_TEST_RESULTS.md
│
├── mssql/                          # Tests del módulo mssql
│   ├── test_mssql.py
│   ├── run_all_mssql_tests.py
│   └── setup_test_mssql.py
│
├── hana/                           # Tests del módulo hana
│   ├── test_hana.py
│   └── setup_test_hana.py
│
├── sapb1sl/                        # Tests del módulo sapb1sl
│   └── example_businesspartners.py
│
├── sat/                            # Tests del módulo sat
│   ├── example_sat_cfdi.py
│   ├── example_validators.py
│   └── test_csf_validator.py
│
├── postgres/                       # Tests del módulo postgres
│   └── test_postgres.py
│
├── redis/                          # Tests del módulo redis
│   └── test_redis.py
│
└── whatsapp/                       # Tests del módulo whatsapp
    └── test_whatsapp.py
```

## 🧪 Pruebas Disponibles

### Pruebas MSSQL ([mssql/test_mssql.py](mssql/test_mssql.py))

Script de pruebas completo para el módulo **mssql**.

**Categorías de pruebas:**
- **DML (10 pruebas)**: INSERT, INSERT_MANY, SELECT, SELECT_ONE, EXISTS, COUNT, UPDATE, UPSERT, DELETE
- **DDL (9 pruebas)**: DATABASE_EXISTS, TABLE_EXISTS, CREATE_TABLE, GET_TABLE_COLUMNS, CREATE_INDEX, EXECUTE_DDL, TRUNCATE_TABLE, DROP_INDEX, DROP_TABLE
- **DCL (8 pruebas)**: CREATE_LOGIN, LOGIN_EXISTS, CREATE_USER, USER_EXISTS, GRANT_PERMISSION, GET_USER_PERMISSIONS, ADD_USER_TO_ROLE, GET_USER_ROLES
- **Gestión de Conexiones (5 pruebas)**: GET_ACTIVE_CONNECTIONS, GET_CONNECTION_COUNT, KILL_ALL_CONNECTIONS

**Total:** 33 pruebas

**Uso:**
```bash
# Modo interactivo (solicita confirmación)
python paquetes/tests/mssql/test_mssql.py

# Requiere base de datos: test_python
# Se puede crear ejecutando: python paquetes/tests/mssql/setup_test_mssql.py
```

**Cobertura:**
- ✓ Operaciones DML básicas y avanzadas
- ✓ Operaciones DDL (tablas, índices, vistas)
- ✓ Gestión de usuarios, logins y permisos (DCL)
- ✓ Monitoreo y administración de conexiones

---

### Pruebas SAP HANA ([hana/test_hana.py](hana/test_hana.py))

Script de pruebas completo para el módulo **hana** (SAP HANA).

**Categorías de pruebas:**
- **DML (10 pruebas)**: INSERT, INSERT_MANY, SELECT, SELECT_ONE, EXISTS, COUNT, UPDATE, UPSERT, DELETE
- **DDL (8 pruebas)**: SCHEMA_EXISTS, TABLE_EXISTS, CREATE_TABLE (COLUMN), GET_TABLE_COLUMNS, CREATE_INDEX, TRUNCATE_TABLE, DROP_INDEX, DROP_TABLE
- **DCL (7 pruebas)**: CREATE_USER, USER_EXISTS, GRANT_PERMISSION, GET_USER_PERMISSIONS, CREATE_ROLE, GRANT_ROLE, GET_USER_ROLES
- **Gestión de Conexiones (2 pruebas)**: GET_ACTIVE_CONNECTIONS, GET_CONNECTION_COUNT

**Total:** 28 pruebas

**Uso:**
```bash
# Modo interactivo (solicita confirmación)
python paquetes/tests/hana/test_hana.py

# ⚠️ ADVERTENCIA: Solo ejecutar en ambiente de desarrollo
# Requiere schema: TEST_PYTHON
# Se puede crear ejecutando: python paquetes/tests/hana/setup_test_hana.py
```

**Cobertura:**
- ✓ Operaciones DML en SAP HANA
- ✓ Tablas COLUMN store (optimizadas para analítica)
- ✓ Gestión de usuarios, roles y permisos en HANA
- ✓ Monitoreo de conexiones activas

---

### Pruebas PostgreSQL ([postgres/test_postgres.py](postgres/test_postgres.py))

Script de pruebas para el módulo **postgres** (PostgreSQL).

**Pruebas incluidas:**
- Conexión a PostgreSQL
- Operaciones DML básicas (INSERT, SELECT, UPDATE, DELETE)
- Creación de tablas

**Uso:**
```bash
# Desde el contenedor (recomendado)
docker exec api-mcp python3 -m paquetes.tests.postgres.test_postgres

# O directamente desde /app
docker exec api-mcp python3 paquetes/tests/postgres/test_postgres.py
```

**Requisitos:**
- PostgreSQL accesible
- Variables de entorno configuradas
- Librería `psycopg2-binary` instalada

---

### Pruebas Redis ([redis/test_redis.py](redis/test_redis.py))

Script de pruebas para el módulo **redis**.

**Pruebas incluidas:**
- Conexión a Redis
- Operaciones básicas (SET, GET, DELETE)
- Operaciones de caché
- Hashes
- Listas
- Conjuntos (Sets)
- Contadores

**Uso:**
```bash
# Desde el contenedor (recomendado)
docker exec api-mcp python3 -m paquetes.tests.redis.test_redis

# O directamente desde /app
docker exec api-mcp python3 paquetes/tests/redis/test_redis.py
```

**Requisitos:**
- Redis accesible
- Variables de entorno configuradas
- Librería `redis` instalada

---

### Pruebas WhatsApp ([whatsapp/test_whatsapp.py](whatsapp/test_whatsapp.py))

Script de pruebas para el módulo **whatsapp** (Evolution API).

**Pruebas incluidas:**
- Conexión a Evolution API
- Listado de instancias
- Creación de instancia
- Generación de QR code para vinculación
- Verificación de estado de conexión
- Formateo de números de teléfono

**Uso:**
```bash
# Desde el contenedor (recomendado)
docker exec api-mcp python3 -m paquetes.tests.whatsapp.test_whatsapp

# O directamente desde /app
docker exec api-mcp python3 paquetes/tests/whatsapp/test_whatsapp.py
```

**Requisitos:**
- Evolution API corriendo (evolution-api-mcp)
- Librería `requests` instalada

**Cobertura:**
- ✓ Cliente Python para Evolution API
- ✓ Creación y gestión de instancias
- ✓ Generación de QR codes
- ✓ Formateo y validación de números

---

### Ejecutor Automático MSSQL ([mssql/run_all_mssql_tests.py](mssql/run_all_mssql_tests.py))

Script que ejecuta **TODAS** las pruebas de MSSQL automáticamente sin interacción del usuario.

**Uso:**
```bash
python paquetes/tests/mssql/run_all_mssql_tests.py
```

**Características:**
- ✓ Ejecución automática de todas las categorías
- ✓ Sin confirmaciones interactivas
- ✓ Reporte completo de resultados
- ✓ Ideal para CI/CD

---

## 🔧 Scripts de Configuración

### Configuración MSSQL ([mssql/setup_test_mssql.py](mssql/setup_test_mssql.py))

Crea y configura la base de datos `test_python` en SQL Server para pruebas.

**Funciones:**
- Verifica si existe la BD `test_python`
- Opción para recrear la BD si ya existe
- Crea 3 tablas de ejemplo:
  - `test_clientes` (clientes de prueba)
  - `test_productos` (productos de prueba)
  - `test_ventas` (ventas de prueba)

**Uso:**
```bash
python paquetes/tests/mssql/setup_test_mssql.py

# Comandos disponibles:
python paquetes/tests/mssql/setup_test_mssql.py        # Crear/configurar BD
python paquetes/tests/mssql/setup_test_mssql.py info   # Ver información de la BD
python paquetes/tests/mssql/setup_test_mssql.py drop   # Eliminar BD (requiere confirmación)
```

**Tablas creadas:**
```sql
test_clientes:
  - id (INT IDENTITY)
  - nombre (NVARCHAR(100))
  - email (NVARCHAR(100))
  - telefono (NVARCHAR(20))
  - activo (BIT)
  - fecha_registro (DATETIME)

test_productos:
  - id (INT IDENTITY)
  - codigo (NVARCHAR(50))
  - nombre (NVARCHAR(100))
  - descripcion (NVARCHAR(MAX))
  - precio (DECIMAL(18,2))
  - stock (INT)
  - activo (BIT)
  - fecha_creacion (DATETIME)

test_ventas:
  - id (INT IDENTITY)
  - cliente_id (INT)
  - producto_id (INT)
  - cantidad (INT)
  - precio_unitario (DECIMAL(18,2))
  - total (DECIMAL(18,2))
  - fecha_venta (DATETIME)
```

---

### Configuración SAP HANA ([hana/setup_test_hana.py](hana/setup_test_hana.py))

Crea y configura el schema `TEST_PYTHON` en SAP HANA para pruebas.

**Funciones:**
- Verifica si existe el schema `TEST_PYTHON`
- Opción para recrear el schema si ya existe
- Crea 3 tablas de ejemplo (COLUMN store):
  - `TEST_CLIENTES` (clientes de prueba)
  - `TEST_PRODUCTOS` (productos de prueba)
  - `TEST_VENTAS` (ventas de prueba)
- Opción para crear usuario de prueba con permisos

**Uso:**
```bash
python paquetes/tests/hana/setup_test_hana.py

# Comandos disponibles:
python paquetes/tests/hana/setup_test_hana.py        # Crear/configurar schema
python paquetes/tests/hana/setup_test_hana.py info   # Ver información del schema
python paquetes/tests/hana/setup_test_hana.py drop   # Eliminar schema (requiere confirmación)
```

**⚠️ ADVERTENCIA:** Este script modifica objetos en SAP HANA. Solo ejecutar en ambiente de desarrollo.

**Tablas creadas (COLUMN store):**
```sql
TEST_CLIENTES:
  - ID (INTEGER IDENTITY)
  - NOMBRE (NVARCHAR(100))
  - EMAIL (NVARCHAR(100))
  - TELEFONO (NVARCHAR(20))
  - ACTIVO (TINYINT)
  - FECHA_REGISTRO (TIMESTAMP)

TEST_PRODUCTOS:
  - ID (INTEGER IDENTITY)
  - CODIGO (NVARCHAR(50))
  - NOMBRE (NVARCHAR(100))
  - DESCRIPCION (NCLOB)
  - PRECIO (DECIMAL(18,2))
  - STOCK (INTEGER)
  - ACTIVO (TINYINT)
  - FECHA_CREACION (TIMESTAMP)

TEST_VENTAS:
  - ID (INTEGER IDENTITY)
  - CLIENTE_ID (INTEGER)
  - PRODUCTO_ID (INTEGER)
  - CANTIDAD (INTEGER)
  - PRECIO_UNITARIO (DECIMAL(18,2))
  - TOTAL (DECIMAL(18,2))
  - FECHA_VENTA (TIMESTAMP)
```

---

## ⚙️ Requisitos

### Variables de Entorno

Las pruebas leen la configuración del archivo `/infraestructura/.env`:

```env
# MSSQL
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_USER=sa
MSSQL_PASSWORD=tu_password
MSSQL_DATABASE=master

# SAP HANA
SAP_HANA_HOST=sap.empresa.local
SAP_HANA_PORT=30015
SAP_HANA_USER=B1ADMIN
SAP_HANA_PASSWORD=tu_password
```

Ver [README de paquetes](../README.md#-configuración) para más detalles.

### Dependencias

```bash
# Para pruebas MSSQL
pip install pyodbc

# Para pruebas SAP HANA
pip install hdbcli
```

### Permisos

**MSSQL:**
- Acceso a base de datos `master` (para crear BD)
- Permisos CREATE DATABASE
- Para pruebas DCL: permisos de administrador (CREATE LOGIN, CREATE USER)

**SAP HANA:**
- Acceso al servidor HANA
- Permisos CREATE SCHEMA
- Para pruebas DCL: permisos de administrador (CREATE USER, CREATE ROLE)

---

## 🚀 Ejecución Rápida

### Configuración Inicial

```bash
# 1. Configurar ambiente MSSQL
cd /software/app
python paquetes/tests/mssql/setup_test_mssql.py

# 2. Configurar ambiente SAP HANA (opcional)
python paquetes/tests/hana/setup_test_hana.py
```

### Ejecutar Pruebas

```bash
# Pruebas MSSQL (interactivo)
python paquetes/tests/mssql/test_mssql.py

# Pruebas MSSQL (automático)
python paquetes/tests/mssql/run_all_mssql_tests.py

# Pruebas SAP HANA (interactivo)
python paquetes/tests/hana/test_hana.py
```

---

## 📊 Resultados Esperados

### MSSQL

```
✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE

Estadísticas:
  - DML: 10 pruebas ✓
  - DDL: 9 pruebas ✓
  - Gestión de Conexiones: 5 pruebas ✓
  - DCL: 8 pruebas ✓ (requiere permisos admin)

Total: 33/33 pruebas exitosas
```

### SAP HANA

```
✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE

Estadísticas:
  - DML: 10 pruebas ✓
  - DDL: 8 pruebas ✓
  - Gestión de Conexiones: 2 pruebas ✓
  - DCL: 7 pruebas ✓ (requiere permisos admin)

Total: 28/28 pruebas exitosas
```

---

## 🔍 Solución de Problemas

### Error: "No se puede conectar a la base de datos"

**Solución:** Verifica las variables de entorno en `/infraestructura/.env`

```bash
# Verificar configuración
cat /infraestructura/.env | grep MSSQL
cat /infraestructura/.env | grep SAP_HANA
```

### Error: "Database 'test_python' does not exist"

**Solución:** Ejecuta el script de configuración:

```bash
python paquetes/tests/mssql/setup_test_mssql.py
```

### Error: "Schema 'TEST_PYTHON' does not exist"

**Solución:** Ejecuta el script de configuración de HANA:

```bash
python paquetes/tests/hana/setup_test_hana.py
```

### Las Pruebas DCL Fallan

**Causa:** Las pruebas DCL requieren permisos de administrador.

**Solución:**
- Ejecuta con un usuario que tenga permisos de administrador
- O omite las pruebas DCL cuando se te pregunte

### Error: "ModuleNotFoundError: No module named 'mssql'"

**Causa:** El path no está configurado correctamente.

**Solución:** Asegúrate de estar en el directorio correcto:

```bash
cd /software/app
python paquetes/tests/mssql/test_mssql.py
```

---

## 📚 Documentación Relacionada

- [Módulo MSSQL](../mssql/README.md)
- [Módulo hana](../hana/README.md)
- [Documentación de Paquetes](../README.md) - Configuración, portabilidad y uso

---

## 🏗️ Arquitectura de las Pruebas

### Estructura de Clases de Prueba

Todas las pruebas siguen la misma estructura:

```python
class TestResult:
    """Clase para rastrear resultados de pruebas"""
    - passed: int
    - failed: int
    - errors: list

    - record_pass(test_name)
    - record_fail(test_name, error)
    - summary()

def run_test(func, test_name, result):
    """Ejecuta una prueba y registra el resultado"""

def test_dml():
    """Pruebas de Data Manipulation Language"""

def test_ddl():
    """Pruebas de Data Definition Language"""

def test_dcl():
    """Pruebas de Data Control Language"""

def test_connections():
    """Pruebas de gestión de conexiones"""
```

### Convenciones

1. **Nombres de pruebas**: Descriptivos y claros
2. **Aserciones**: Usar `assert` con mensajes claros
3. **Limpieza**: Cada prueba limpia sus propios datos
4. **Independencia**: Las pruebas no dependen entre sí
5. **Confirmaciones**: Las pruebas interactivas solicitan confirmación del usuario

---

## ⚠️ Advertencias Importantes

1. **NO ejecutar en producción**
   - Las pruebas crean, modifican y eliminan objetos en las bases de datos
   - Solo ejecutar en ambientes de desarrollo o prueba

2. **Operaciones destructivas**
   - Los scripts de configuración pueden eliminar bases de datos y schemas existentes
   - Siempre confirmar antes de proceder

3. **Permisos administrativos**
   - Las pruebas DCL requieren permisos elevados
   - No ejecutar con usuarios de solo lectura

4. **SAP HANA**
   - El servidor configurado puede ser de producción
   - Verificar el ambiente antes de ejecutar

---

**Versión:** 1.0.0
**Última actualización:** 2026-01-31
