# Paquetes

Módulos genéricos e independientes para Microsoft SQL Server, SAP HANA, PostgreSQL, Redis, SAP B1 Service Layer, LDAP/Active Directory, Facturación Electrónica (CFDI/SAT) y Comunicación.

## 📊 Resumen Ejecutivo

**Módulos totales:** 11 módulos principales + 3 herramientas genéricas
**Funciones totales:** 294+ funciones

### Desglose por Módulo

| Módulo | Funciones | Descripción |
|--------|-----------|-------------|
| **mssql** | 49 | DML (14) + DDL (12) + DCL (23) |
| **hana** | 39 | DML (13) + DDL (10) + DCL (16) |
| **postgres** | 50 | DML (13) + DDL (14) + DCL (23) |
| **redis** | 33 | Strings, cache, hashes, lists, sets, counters, utils |
| **sapb1sl** | 17 | Auth (5) + CRUD (7) + Queries (5) |
| **auth** | 19 | Endpoints (6) + Middleware (3) + Sessions (10) |
| **ldap** | 37 | Connection (3) + Auth (3) + Search (8) + Users (8) + Groups (8) + OUs (7) |
| **sat** | 34 | CFDI (31) + Validador CSF (3) |
| **email** | 2 | Envío de correos con SMTP |
| **evolution** | 14 | Instancias (7) + Mensajes (4) + Utilidades (3) |
| **whatsapp** | 16 | Cliente Evolution API (métodos) |

### Cobertura Funcional

Los módulos cubren las siguientes áreas:

- **Bases de datos**: MSSQL, HANA, PostgreSQL
- **Caché**: Redis
- **ERP**: SAP Business One Service Layer
- **Autenticación**: Auth, LDAP/Active Directory
- **Facturación**: SAT/CFDI + Validador CSF
- **Comunicación**: Email, WhatsApp, Evolution API

## 📋 Contenido

- [Descripción](#-descripción)
- [Módulos Disponibles](#-módulos-disponibles)
- [Herramientas MSSQL](#-herramientas-mssql)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Portabilidad](#-portabilidad)
- [Pruebas](#-pruebas)
- [API de Conexión](#-api-de-conexión)
- [Solución de Problemas](#-solución-de-problemas)

---

## 📦 Descripción

Los paquetes `mssql`, `hana`, `sapb1sl`, `auth`, `ldap`, `sat`, `email` y `whatsapp` son **módulos completamente genéricos e independientes** que pueden ser utilizados en cualquier proyecto Python sin depender de archivos de configuración específicos.

### Características

✓ **Independientes**: No dependen de `config.py` ni ningún otro archivo de configuración
✓ **Flexibles**: Aceptan credenciales como parámetros o leen de variables de entorno
✓ **Portables**: Pueden copiarse a cualquier proyecto y funcionar inmediatamente
✓ **Sin valores por defecto**: El usuario debe proporcionar las credenciales explícitamente
✓ **Arquitectura SQL estándar**: Organizados en DML, DDL y DCL

---

## 🎯 Módulos Disponibles

### [mssql](mssql/)

Módulo completo para Microsoft SQL Server con 49 funciones.

**Estructura:**
```
mssql/
├── __init__.py          # Exporta todas las funciones
├── mssql_dml.py         # DML: SELECT, INSERT, UPDATE, DELETE (14 funciones)
├── mssql_ddl.py         # DDL: CREATE, DROP, ALTER (12 funciones)
├── mssql_dcl.py         # DCL: GRANT, REVOKE, usuarios, roles (23 funciones)
└── README.md            # Documentación completa
```

**Documentación:** [mssql/README.md](mssql/README.md)

---

### [hana](hana/)

Módulo completo para SAP HANA con 39 funciones.

**Estructura:**
```
hana/
├── __init__.py          # Exporta todas las funciones
├── hana_dml.py          # DML: SELECT, INSERT, UPDATE, DELETE (13 funciones)
├── hana_ddl.py          # DDL: CREATE, DROP, ALTER (10 funciones)
├── hana_dcl.py          # DCL: GRANT, REVOKE, usuarios, roles (16 funciones)
└── README.md            # Documentación completa
```

**Características especiales:**
- Soporte para tablas COLUMN store (analítica)
- Soporte para tablas ROW store (transaccional)
- Gestión avanzada de schemas con filtros personalizables
- Funciones para listar y filtrar schemas SAP B1

**Documentación:** [hana/README.md](hana/README.md)

---

### [postgres](postgres/)

Módulo completo para PostgreSQL con 50 funciones.

**Estructura:**
```
postgres/
├── __init__.py          # Exporta todas las funciones
├── postgres_dml.py      # DML: SELECT, INSERT, UPDATE, DELETE (13 funciones)
├── postgres_ddl.py      # DDL: CREATE, DROP, ALTER (14 funciones)
├── postgres_dcl.py      # DCL: GRANT, REVOKE, roles (23 funciones)
└── README.md            # Documentación completa
```

**Características especiales:**
- Soporte completo para schemas
- Operaciones UPSERT nativas (INSERT ... ON CONFLICT)
- Gestión de roles y permisos granulares
- Retorna resultados como diccionarios
- Compatible con PostgreSQL 10+

**Documentación:** [postgres/README.md](postgres/README.md)

---

### [redis](redis/)

Módulo completo para Redis con 33 funciones.

**Estructura:**
```
redis/
├── __init__.py              # Exporta todas las funciones
├── redis_connection.py      # Todas las operaciones de Redis
└── README.md                # Documentación completa
```

**Características especiales:**
- Operaciones básicas (GET, SET, DELETE, EXPIRE)
- Operaciones de caché con TTL
- Hashes para objetos estructurados
- Listas para colas y logs
- Conjuntos (Sets) para colecciones únicas
- Contadores atómicos
- Serialización automática de JSON

**Documentación:** [redis/README.md](redis/README.md)

---

### [sapb1sl](sapb1sl/)

Cliente REST API para SAP Business One Service Layer con 17 funciones.

**Estructura:**
```
sapb1sl/
├── __init__.py          # Exporta todas las funciones
├── sl_auth.py           # Autenticación y sesiones (5 funciones)
├── sl_crud.py           # CRUD: GET, POST, PATCH, DELETE (7 funciones)
├── sl_queries.py        # Queries OData (5 funciones)
└── README.md            # Documentación completa
```

**Características especiales:**
- Autenticación automática con gestión de sesiones
- Soporte completo para OData ($filter, $select, $expand, etc.)
- CRUD genérico para todas las entidades de SAP B1
- Caché de sesión para optimizar rendimiento

**Documentación:** [sapb1sl/README.md](sapb1sl/README.md)

---

### [auth](auth/)

Sistema de autenticación con session tokens y sliding expiration con 19 funciones.

**Estructura:**
```
auth/
├── __init__.py              # Exporta todas las funciones
├── sessions.py              # Gestión de sesiones en MSSQL (10 funciones)
├── middleware.py            # Decoradores para proteger rutas (3 funciones)
├── endpoints.py             # Helpers para login/logout (6 funciones)
├── storage_mssql.py         # Implementación de almacenamiento MSSQL
├── storage.py               # Interfaz de almacenamiento
└── README.md                # Documentación completa

Ejemplos completos (en tests/auth/):
├── example_validators.py    # Ejemplos de validadores de usuarios
├── example_auth_flask.py    # Ejemplo completo con Flask
└── example_auth_fastapi.py  # Ejemplo completo con FastAPI
```

**Características especiales:**
- Session tokens almacenados en MSSQL con UUID
- Sliding expiration (renovación automática en cada petición)
- Límite configurable de sesiones activas por usuario
- Soporte para scopes/permisos granulares
- Decoradores `@require_auth()` para Flask y FastAPI
- Helpers para crear endpoints automáticamente
- Validador de usuarios configurable (LDAP, BD, etc.)

**Ejemplos de uso:**
```bash
# Ejecutar ejemplo con Flask
python paquetes/tests/auth/example_auth_flask.py

# Ejecutar ejemplo con FastAPI
python paquetes/tests/auth/example_auth_fastapi.py
```

**Documentación:** [auth/README.md](auth/README.md)

---

### [ldap](ldap/)

Módulo completo para LDAP y Active Directory con 37 funciones.

**Estructura:**
```
ldap/
├── __init__.py              # Exporta todas las funciones
├── ldap_connection.py       # Gestión de conexiones (3 funciones)
├── ldap_auth.py             # Autenticación y validación (3 funciones)
├── ldap_search.py           # Búsquedas (8 funciones)
├── ldap_users.py            # Gestión de usuarios (8 funciones)
├── ldap_groups.py           # Gestión de grupos (8 funciones)
├── ldap_ous.py              # Gestión de OUs (7 funciones)
└── README.md                # Documentación completa
```

**Características especiales:**
- Soporte para LDAP y LDAPS (SSL/TLS) con certificados autofirmados
- Compatible con Active Directory y OpenLDAP
- Autenticación de usuarios con credenciales
- Búsqueda de usuarios por atributos (sAMAccountName, cn, mail, etc.)
- Gestión completa CRUD de usuarios, grupos y OUs
- Consulta de grupos y membresías
- Validación de contraseñas y bloqueos
- Gestión de información de usuarios (nombre, email, teléfono, etc.)

**Ejemplos de uso:**
```bash
# Ejemplo básico (consultas, búsqueda, autenticación)
python paquetes/tests/ldap/example_ldap_basic.py

# Ejecutar pruebas desde contenedor
docker exec -w /app api-mcp python3 paquetes/tests/ldap/test_ldaps_simple.py
```

**Documentación:** [ldap/README.md](ldap/README.md) | [ldap/CONFIGURATION.md](ldap/CONFIGURATION.md)

---

### [sat](sat/)

Módulo completo para Facturación Electrónica (CFDI) y servicios del SAT con 34 funciones.

**Estructura:**
```
sat/
├── __init__.py              # Exporta todas las funciones
├── cfdi_generator.py        # Generación de CFDI (5 funciones)
├── cfdi_validator.py        # Validación de CFDI (5 funciones)
├── cfdi_stamping.py         # Timbrado con PAC (6 funciones)
├── sat_download.py          # Descarga masiva SAT (5 funciones)
├── rfc_validator.py         # Validación RFC y listas (6 funciones)
├── csf.py                   # Constancia Situación Fiscal (4 funciones)
├── csf_validator.py         # Validador de CSF en PDF (3 funciones)
└── README.md                # Documentación completa
```

**Características especiales:**
- Generación de CFDI 4.0 (Ingreso, Egreso, Pago, Nómina)
- Validación de estructura XML según especificaciones del SAT
- Timbrado con múltiples PACs (Finkok, SW Sapien, Diverza)
- Descarga masiva automatizada desde portal del SAT
- Validación de RFC y verificación en listas negras (69-B)
- Consulta de Constancia de Situación Fiscal (CSF)
- Verificación de sellos digitales
- Cancelación de CFDIs

**Ejemplos de uso:**
```bash
# Ejemplo completo de facturación electrónica
python paquetes/tests/sat/example_sat_cfdi.py
```

**Documentación:** [sat/README.md](sat/README.md)

---

### [email](email/)

Módulo para envío de correos electrónicos con soporte para postfix local y relay SMTP externo.

**Estructura:**
```
email/
├── __init__.py              # Exporta todas las funciones
├── email_sender.py          # Envío de correos (2 funciones)
└── README.md                # Documentación completa
```

**Características especiales:**
- Dos modos de operación: local (postfix) y relay (SMTP externo)
- Soporte para múltiples destinatarios
- Adjuntos de archivos
- Correos en HTML o texto plano
- Configuración flexible por parámetros o variables de entorno
- Compatible con Gmail, Outlook, servidores corporativos

**Ejemplos de uso:**
```bash
# Ejemplo completo de envío de correos
python paquetes/tests/example_email.py
```

**Documentación:** [email/README.md](email/README.md)

---

### [evolution](evolution/)

Cliente genérico para Evolution API - Sistema multi-instancia de WhatsApp con 14 funciones.

**Estructura:**
```
evolution/
├── __init__.py              # Exporta todas las funciones
├── evolution_client.py      # Cliente principal (14 funciones)
└── README.md                # Documentación completa
```

**Características especiales:**
- Gestión de instancias: crear, listar, eliminar, reiniciar
- Envío de mensajes: texto, imágenes, documentos, multimedia
- Verificación de estado y conexión
- Obtención de QR codes para vinculación
- Cliente genérico y portable (sin dependencias de proyecto)
- Compatible con Evolution API v2.3.6+

**Ejemplos de uso:**
```python
from evolution import get_evolution_client

# Crear cliente
client = get_evolution_client()

# Listar instancias
instances = client.list_instances()

# Crear nueva instancia
result = client.create_instance("ventas")
print(result['qrcode']['code'])  # QR code

# Enviar mensaje
client.send_text("ventas", "5215512345678", "Hola!")
```

**Documentación:** [evolution/README.md](evolution/README.md)

---

### [whatsapp](whatsapp/)

Módulo para envío de mensajes de WhatsApp usando Evolution API con 16 métodos.

**Estructura:**
```
whatsapp/
├── __init__.py              # Exporta client y router
├── client.py                # Cliente Python para Evolution API (16 métodos)
├── router.py                # Router FastAPI con endpoints REST
├── README.md                # Documentación completa
└── INTEGRATION_EXAMPLES.md  # Ejemplos de integración
```

**Características especiales:**
- Cliente Python completo para Evolution API v2.3.6
- Router FastAPI con endpoints REST
- Envío de mensajes de texto, imágenes y documentos
- Gestión de múltiples instancias de WhatsApp
- Formateo automático de números de teléfono
- Verificación de estado de conexión
- Generación de QR codes para vinculación
- Soporte para webhooks y eventos

**Ejemplos de uso:**
```python
# Uso directo del cliente
from paquetes.whatsapp import client

client.send_text("instancia", "5215512345678", "Hola!")

# O usar endpoints REST (agregar router a FastAPI)
from paquetes.whatsapp import router
app.include_router(router)
```

**Documentación:** [whatsapp/README.md](whatsapp/README.md)

---

### [tests](tests/)

Suite completa de pruebas con 61 pruebas (33 MSSQL + 28 HANA).

**Contenido:**
```
tests/
├── README.md                 # Documentación de pruebas
├── auth/                     # Tests y ejemplos del módulo auth
├── ldap/                     # Tests y ejemplos del módulo ldap
├── mssql/                    # Tests del módulo mssql
│   ├── test_mssql.py        # 33 pruebas para MSSQL
│   ├── run_all_mssql_tests.py   # Ejecutor automático
│   └── setup_test_mssql.py  # Setup de BD de pruebas
├── hana/                     # Tests del módulo hana
│   ├── test_hana.py         # 28 pruebas para SAP HANA
│   └── setup_test_hana.py   # Setup de schema de pruebas
├── sapb1sl/                  # Tests del módulo sapb1sl
├── sat/                      # Tests del módulo sat
└── whatsapp/                 # Tests del módulo whatsapp
```

**Documentación:** [tests/README.md](tests/README.md)

---

## 🛠️ Herramientas MSSQL

### [mssql_attach_db.py](mssql_attach_db.py)

Herramienta genérica para adjuntar bases de datos MSSQL desde archivos .mdf y .ldf

**Uso desde línea de comandos:**
```bash
# Adjuntar base de datos progex (default)
python -m paquetes.mssql_attach_db

# Adjuntar base de datos personalizada
python -m paquetes.mssql_attach_db -d mi_bd

# Con rutas personalizadas
python -m paquetes.mssql_attach_db -d ventas \
    --mdf /var/opt/mssql/data/ventas.mdf \
    --ldf /var/opt/mssql/data/ventas_log.ldf
```

**Uso como módulo Python:**
```python
from paquetes.mssql_attach_db import attach_database, attach_progex

# Genérico
attach_database(
    database_name='ventas',
    mdf_path='/var/opt/mssql/data/ventas.mdf',
    ldf_path='/var/opt/mssql/data/ventas_log.ldf'
)

# Conveniencia para progex
attach_progex()
```

---

### [mssql_imp_exp_tbl_vw.py](mssql_imp_exp_tbl_vw.py)

Herramienta para exportar estructura de tablas y vistas de MSSQL a archivo .def

**Uso desde línea de comandos:**
```bash
# Exportar estructura de progex (genera paquetes/tbl_vw.progex.def)
python -m paquetes.mssql_imp_exp_tbl_vw exp progex

# Exportar con nombre personalizado (genera paquetes/mi_estructura.def)
python -m paquetes.mssql_imp_exp_tbl_vw exp progex mi_estructura

# Importar estructura a nueva BD (busca automáticamente .def en paquetes/)
python -m paquetes.mssql_imp_exp_tbl_vw imp test_db

# Importar especificando archivo .def
python -m paquetes.mssql_imp_exp_tbl_vw imp test_db tbl_vw.progex.def

# Importar recreando la BD destino (elimina y recrea)
python -m paquetes.mssql_imp_exp_tbl_vw imp test_db --recrear
```

**Uso como módulo Python:**
```python
from paquetes.mssql_imp_exp_tbl_vw import exportar_estructura, importar_estructura

# Exportar (genera en paquetes/ por defecto)
exportar_estructura(database='progex')

# Exportar con ruta personalizada
exportar_estructura(database='progex', output_file='/tmp/estructura.def')

# Importar
importar_estructura(database_destino='test_db', archivo_estructura='paquetes/tbl_vw.progex.def')
```

---

### [sat/csf_validator.py](sat/csf_validator.py)

Módulo genérico y portable para validar archivos PDF de Constancias de Situación Fiscal (CSF) del SAT de México. Parte del paquete SAT.

**Funcionalidades:**
- ✅ Extracción de datos de PDFs de CSF
- ✅ Validación de formato de RFC
- ✅ Consulta de situación fiscal en el SAT
- ✅ Verificación en listas negras (69-B)
- ✅ Generación de reportes HTML profesionales
- ✅ Completamente portable y genérico

**Uso desde línea de comandos:**
```bash
# Validación completa con reporte HTML (desde contenedor)
docker exec -w /app api-mcp python3 paquetes/tests/sat/test_csf_validator.py archivo.pdf XAXX010101000

# Desde el host
cd software/app
python3 paquetes/tests/sat/test_csf_validator.py archivo.pdf XAXX010101000
```

**Uso como módulo Python:**
```python
from paquetes.sat.csf_validator import validate_csf_full

# Validación completa con reporte HTML automático
result = validate_csf_full(
    pdf_file='constancia.pdf',
    expected_rfc='XAXX010101000'
)

if result['success']:
    data = result['validation_data']
    print(f"RFC: {data['rfc']}")
    print(f"Estado: {data['estado']}")
    print(f"Seguro transaccionar: {data['seguro_transaccionar']}")
    print(f"Reporte HTML: {result['html_file']}")
```

**Funciones disponibles:**
- `validate_csf_from_pdf()` - Valida PDF de CSF y extrae información
- `generate_html_report()` - Genera reporte HTML profesional
- `validate_csf_full()` - Proceso completo de validación + reporte HTML

**Documentación:** Integrada en [sat/README.md](sat/README.md) sección "Validador de CSF"

---

## 🔧 Instalación

### Dependencias

```bash
# API Framework y Servidor
pip install fastapi==0.109.0 uvicorn[standard]==0.27.0 starlette==0.35.1
pip install pydantic==2.5.3 pydantic-settings==2.1.0

# Autenticación y Seguridad
pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4
pip install bcrypt==5.0.0 cryptography==46.0.3

# Bases de Datos
pip install pyodbc==5.0.1      # SQL Server
pip install hdbcli==2.19.21    # SAP HANA

# LDAP/Active Directory
pip install ldap3==2.9.1

# Procesamiento de Archivos
pip install openpyxl==3.1.2           # Excel
pip install pdfplumber==0.11.9        # PDF (para CSF y documentos)
pip install reportlab==4.4.9          # Generación de PDFs
pip install pillow==12.1.0            # Procesamiento de imágenes

# HTTP y Networking
pip install httpx==0.26.0 certifi==2026.1.4

# Utilidades
pip install python-multipart==0.0.6 python-dotenv==1.2.1 PyYAML==6.0.3

# Instalación completa (todas las dependencias)
pip install -r infraestructura/Docker/requirements.txt
```

**Total de dependencias:** 47 paquetes

Ver el archivo completo: [infraestructura/Docker/requirements.txt](../../infraestructura/Docker/requirements.txt)

---

## ⚙️ Configuración

### Variables de Entorno

Los módulos son genéricos y **NO tienen valores por defecto**. Debes configurar las variables de entorno.

#### Microsoft SQL Server (módulo `mssql`)

```env
# Host del servidor SQL Server
MSSQL_HOST=localhost

# Puerto (generalmente 1433)
MSSQL_PORT=1433

# Usuario de SQL Server
MSSQL_USER=sa

# Contraseña del usuario
MSSQL_PASSWORD=tu_password_aqui

# Base de datos por defecto
MSSQL_DATABASE=master
```

#### SAP HANA (módulo `hana`)

```env
# Host del servidor SAP HANA
SAP_HANA_HOST=sap.empresa.local

# Puerto (generalmente 30015)
SAP_HANA_PORT=30015

# Usuario de SAP HANA
SAP_HANA_USER=B1ADMIN

# Contraseña del usuario
SAP_HANA_PASSWORD=tu_password_aqui
```

#### PostgreSQL (módulo `postgres`)

```env
# Host del servidor PostgreSQL
POSTGRES_HOST=localhost

# Puerto (generalmente 5432)
POSTGRES_PORT=5432

# Usuario de PostgreSQL
POSTGRES_USER=postgres

# Contraseña del usuario
POSTGRES_PASSWORD=tu_password_aqui

# Base de datos por defecto
POSTGRES_DATABASE=postgres
```

#### Redis (módulo `redis`)

```env
# Host del servidor Redis
REDIS_HOST=localhost

# Puerto (generalmente 6379)
REDIS_PORT=6379

# Número de base de datos (0-15)
REDIS_DB=0

# Contraseña (opcional si no tiene contraseña configurada)
REDIS_PASSWORD=tu_password_aqui
```

#### LDAP/Active Directory (módulo `ldap`)

```env
# Servidor LDAP (REQUERIDO)
LDAP_SERVER=ldap.empresa.com
LDAP_PORT=389                        # Opcional: 389 para LDAP, 636 para LDAPS
LDAP_USE_SSL=false                   # Opcional: true para LDAPS

# Base DN (OPCIONAL - se deriva automáticamente de LDAP_BIND_DN)
# LDAP_BASE_DN=DC=empresa,DC=com

# Credenciales de administrador (REQUERIDO)
LDAP_BIND_DN=admin@empresa.com       # Formato UPN (recomendado)
# O formato DN: LDAP_BIND_DN=CN=admin,DC=empresa,DC=com
LDAP_BIND_PASSWORD=password_admin

# Autenticación de usuarios (opcional)
LDAP_USER_DN_TEMPLATE=CN={username},OU=Users,DC=empresa,DC=com
LDAP_SEARCH_FILTER=(sAMAccountName={username})  # Para AD
LDAP_AUTH_TYPE=SIMPLE                            # SIMPLE, NTLM, ANONYMOUS
```

**Nota**: `LDAP_BASE_DN` se deriva automáticamente:
- De UPN: `admin@empresa.com` → `DC=empresa,DC=com`
- De DN: `CN=admin,DC=empresa,DC=com` → `DC=empresa,DC=com`

#### Facturación Electrónica/SAT (módulo `sat`)

```env
# Emisor (para generación de CFDI)
SAT_EMISOR_RFC=XAXX010101000
SAT_EMISOR_NOMBRE=MI EMPRESA SA DE CV
SAT_CERTIFICADO_PATH=/ruta/certificado.cer
SAT_KEY_PATH=/ruta/llave.key
SAT_KEY_PASSWORD=password

# PAC (Proveedor para timbrado)
SAT_PAC_PROVIDER=finkok                         # finkok, sw, diverza
SAT_PAC_USERNAME=usuario@empresa.com
SAT_PAC_PASSWORD=password_pac
SAT_PAC_MODE=production                          # test o production

# FIEL (para descarga masiva y CSF)
SAT_FIEL_CER=/ruta/fiel.cer
SAT_FIEL_KEY=/ruta/fiel.key
SAT_FIEL_PASSWORD=password_fiel
```

#### Email (módulo `email`)

```env
# Modo de envío: 'local' (postfix) o 'relay' (SMTP externo)
EMAIL_MODE=local

# Email del remitente por defecto
EMAIL_FROM=sistema@midominio.com

# --- Configuración para modo RELAY (SMTP externo) ---

# Servidor SMTP (Gmail, Outlook, servidor corporativo, etc.)
SMTP_HOST=smtp.gmail.com

# Puerto SMTP (587 para TLS, 465 para SSL, 25 para no cifrado)
SMTP_PORT=587

# Credenciales SMTP
SMTP_USER=mi_cuenta@gmail.com
SMTP_PASSWORD=mi_app_password

# Seguridad
SMTP_USE_TLS=true   # STARTTLS (puerto 587)
SMTP_USE_SSL=false  # SSL directo (puerto 465)
```

**Nota**: Para modo `local`, solo requiere `EMAIL_FROM` y el servicio postfix corriendo.

### Archivo de Configuración

Si usas la aplicación completa, las variables se configuran en: `/infraestructura/.env`

**Ejemplo completo de `.env`:**

```env
# Microsoft SQL Server
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_USER=sa
MSSQL_PASSWORD=MySecurePass123!
MSSQL_DATABASE=progex

# SAP HANA
SAP_HANA_HOST=sap.empresa.local
SAP_HANA_PORT=30015
SAP_HANA_USER=B1ADMIN
SAP_HANA_PASSWORD=SecureHanaPass456!

# SAP Business One Service Layer (opcional)
SAP_B1_SERVICE_LAYER_URL=https://sap.empresa.local:50000/b1s/v1
SAP_B1_USER=manager
SAP_B1_PASSWORD=ManagerPass789!

# Autenticación (módulo auth) - usa MSSQL para almacenar sesiones
JWT_EXPIRATION_MINUTES=30              # Timeout de sesión (default: 30 minutos)
SESIONES_ACTIVAS=2                     # Máximo de sesiones por usuario (default: 2)
AUTH_VALIDATOR_MODULE=paquetes.auth.validators
AUTH_VALIDATOR_FUNCTION=validate_user

# LDAP/Active Directory (módulo ldap)
LDAP_SERVER=ldap.empresa.com
LDAP_PORT=389
LDAP_USE_SSL=false
# LDAP_BASE_DN=DC=empresa,DC=com  # Opcional - se deriva de BIND_DN
LDAP_BIND_DN=admin@empresa.com  # Formato UPN (o CN=admin,DC=empresa,DC=com)
LDAP_BIND_PASSWORD=AdminPassword123!
LDAP_SEARCH_FILTER=(sAMAccountName={username})
LDAP_AUTH_TYPE=SIMPLE

# Email (módulo email)
EMAIL_MODE=local                        # 'local' (postfix) o 'relay' (SMTP)
EMAIL_FROM=sistema@midominio.com        # Remitente por defecto

# Solo para modo relay:
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=cuenta@gmail.com
# SMTP_PASSWORD=app_password
# SMTP_USE_TLS=true
# SMTP_USE_SSL=false
```

### ⚠️ Seguridad

**IMPORTANTE:**

1. **NUNCA** commitear el archivo `.env` al repositorio Git
2. El archivo `.env` debe estar en `.gitignore`
3. Usar contraseñas fuertes para ambientes de producción
4. Rotar las credenciales periódicamente
5. Usar variables de entorno diferentes para desarrollo, staging y producción

---

## 💡 Uso

### Opción 1: Variables de Entorno

```bash
# Configurar variables de entorno
export MSSQL_HOST=localhost
export MSSQL_PORT=1433
export MSSQL_USER=sa
export MSSQL_PASSWORD=mi_password
export MSSQL_DATABASE=mi_db

export SAP_HANA_HOST=sap.empresa.local
export SAP_HANA_PORT=30015
export SAP_HANA_USER=B1ADMIN
export SAP_HANA_PASSWORD=mi_password
```

```python
from paquetes.mssql import select, get_mssql_connection
from paquetes.hana import select as hana_select, get_hana_connection
from paquetes.sapb1sl import query_entities, create_entity
from paquetes.auth import require_auth, login_user
from paquetes.ldap import authenticate_user, search_user_by_username
from paquetes.sat import create_cfdi_ingreso, stamp_cfdi, validate_rfc_format
from paquetes.sat.csf_validator import validate_csf_full
from paquetes.email import send_email, validar_configuracion

# Las funciones leen automáticamente de las variables de entorno
registros_sql = select('mi_tabla', database='mi_db')
registros_hana = hana_select('OITM', schema='SBODEMOUY')

# Autenticación
result = login_user('admin', 'password123')
if result['success']:
    session_id = result['session']['session_id']

# LDAP - Autenticación y búsqueda
if authenticate_user('jperez', 'password123'):
    print("Usuario autenticado en LDAP")

user_info = search_user_by_username('jperez')
if user_info:
    print(f"Usuario: {user_info['cn']}, Email: {user_info['mail']}")

# SAT / Facturación Electrónica
rfc_valido = validate_rfc_format('XAXX010101000')
if rfc_valido['valid']:
    cfdi = create_cfdi_ingreso(emisor, receptor, conceptos, lugar_expedicion='12345')
    if cfdi['success']:
        timbrado = stamp_cfdi(cfdi['xml'])
        print(f"CFDI timbrado. UUID: {timbrado['timbre']['uuid']}")

# CSF - Validación de Constancia de Situación Fiscal
result = validate_csf_full('constancia.pdf', expected_rfc='XAXX010101000')
if result['success']:
    data = result['validation_data']
    print(f"RFC: {data['rfc']}, Estado: {data['estado']}")
    print(f"Seguro transaccionar: {data['seguro_transaccionar']}")
    print(f"Reporte: {result['html_file']}")

# Email - Envío de correos electrónicos
result = send_email(
    para='usuario@ejemplo.com',
    titulo='Notificación del sistema',
    cuerpo='Este es un mensaje automático.',
    de='sistema@midominio.com'
)
if result['success']:
    print(f"Correo enviado a {', '.join(result['destinatarios'])}")
```

### Opción 2: Credenciales Directas

```python
from paquetes.mssql import get_mssql_connection
from paquetes.hana import get_hana_connection

# SQL Server - pasar credenciales directamente
conn_sql = get_mssql_connection(
    database='mi_db',
    host='localhost',
    port=1433,
    user='sa',
    password='mi_password'
)

# SAP HANA - pasar credenciales directamente
conn_hana = get_hana_connection(
    schema='SBODEMOUY',
    host='sap.empresa.local',
    port=30015,
    user='B1ADMIN',
    password='mi_password'
)
```

### Opción 3: Mixta

```python
from paquetes.mssql import get_mssql_connection

# MSSQL_HOST, MSSQL_PORT, MSSQL_USER, MSSQL_PASSWORD se leen del env
# Solo se especifica la base de datos
conn = get_mssql_connection(database='otra_db')
```

---

## 📦 Portabilidad

### Copiar a Otro Proyecto

Los paquetes son completamente independientes y pueden copiarse a cualquier proyecto:

```bash
# Copiar el paquete mssql
cp -r /ruta/a/paquetes/mssql /tu/proyecto/

# Copiar el paquete hana
cp -r /ruta/a/paquetes/hana /tu/proyecto/
```

### Usar en Otro Proyecto

```python
# Importar directamente
from mssql import *
from hana import *

# O usar con credenciales específicas
from mssql import get_mssql_connection

conn = get_mssql_connection(
    database='tu_db',
    host='tu_servidor',
    port=1433,
    user='tu_usuario',
    password='tu_password'
)
```

### Ventajas del Diseño

1. **Portabilidad Total**: Los paquetes funcionan sin modificaciones en cualquier proyecto
2. **Flexibilidad**: Usa variables de entorno, parámetros directos, o una combinación
3. **Sin Dependencias de Configuración**: No necesitan `config.py` específico
4. **Seguridad**: Las credenciales nunca están hardcodeadas
5. **Multi-Entorno**: Fácil de usar en desarrollo, staging y producción

### 📊 Configuración: Tabla CONFIG vs Variables de Ambiente

#### Regla Fundamental
El proyecto separa la configuración en dos niveles:

| Ubicación | Mecanismo | Razón |
|-----------|-----------|-------|
| **`paquetes/`** | Variables de ambiente (`os.getenv()`) | Portabilidad y genericidad |
| **`app/`** | Tabla CONFIG (consultas SQL) | Centralización y auditoría |

#### ✅ Código en `paquetes/` → Variables de Ambiente

Los paquetes **SIEMPRE** usan variables de ambiente para mantener portabilidad:

```python
# paquetes/auth/sessions.py
def get_expiration_minutes():
    return int(os.getenv('JWT_EXPIRATION_MINUTES', '30'))  # ✅ Correcto

# paquetes/mssql/mssql_dml.py
def get_mssql_connection(host=None, database=None):
    host = host or os.getenv('MSSQL_HOST', 'localhost')  # ✅ Correcto
    return pyodbc.connect(...)
```

**Ventajas:**
- Mantiene paquetes independientes de la aplicación
- Permite copiar paquetes a otros proyectos sin cambios
- No requiere acceso a base de datos para funcionar
- Interfaz estándar de configuración (variables de entorno)

#### ✅ Código en `app/` → Tabla CONFIG

La aplicación específica **SIEMPRE** usa tabla CONFIG:

```python
# app/auth_fastapi.py
from paquetes.mssql import select

def get_jwt_expiration():
    result = select('CONFIG',
                   columns=['ConfigValue'],
                   where='ConfigKey = ?',
                   where_params=('jwt_expiration_minutes',))
    return int(result[0]['ConfigValue']) if result else 30  # ✅ Correcto
```

**Estructura de CONFIG:**
```sql
CREATE TABLE CONFIG (
    ConfigKey NVARCHAR(100) PRIMARY KEY,
    ConfigValue NVARCHAR(MAX),
    Description NVARCHAR(500),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedBy NVARCHAR(100)
)
```

**Ventajas:**
- Centraliza configuración de la aplicación
- Auditoría de cambios (UpdatedAt, UpdatedBy)
- Modificación sin reiniciar contenedores
- Documentación inline (Description)
- Historial de configuraciones

#### ❌ Anti-Patrones

**INCORRECTO en app/:**
```python
# app/auth_fastapi.py
def get_jwt_expiration():
    return int(os.getenv('JWT_EXPIRATION_MINUTES', '30'))  # ❌ Usar CONFIG
```

**INCORRECTO en paquetes/:**
```python
# paquetes/auth/sessions.py
def get_expiration_minutes():
    result = select('CONFIG', ...)  # ❌ Usar os.getenv()
    return int(result[0]['ConfigValue'])
```

#### Flujo de Configuración

1. **`.env`** → Define variables de ambiente para Docker/infraestructura
2. **Startup** → App copia valores de .env a tabla CONFIG
3. **Paquetes** → Leen de variables de ambiente (portabilidad)
4. **App** → Lee de tabla CONFIG (centralización)

#### Categorías de Configuración

La tabla CONFIG organiza configuraciones por categoría:

| Categoría | Cantidad | Ejemplos |
|-----------|----------|----------|
| Autenticación | 5 | jwt_algorithm, jwt_expiration_minutes |
| Base de Datos | 4 | mssql_host, mssql_database |
| LDAP | 6 | ldap_server, ldap_port, ldap_use_ssl |
| SAP | 5 | sap_hana_host, sap_b1_service_layer_url |
| Email | 4 | smtp_host, email_from |
| Evolution | 1 | evolution_api_url |
| Aplicación | N | Configuraciones del negocio |

#### Cuándo Usar Cada Mecanismo

**Variables de Ambiente** (`os.getenv()`):
- ✅ Todo el código en `paquetes/`
- ✅ Configuración de infraestructura
- ✅ Credenciales de conexión
- ✅ Cuando se requiere portabilidad

**Tabla CONFIG** (consultas SQL):
- ✅ Todo el código en `app/`
- ✅ Configuración de aplicación
- ✅ Timeouts, límites, reglas de negocio
- ✅ Cuando se requiere auditoría
- ✅ Cuando se quiere modificar sin reiniciar

---

## 🧪 Pruebas

### Configurar Ambientes de Prueba

```bash
# 1. Configurar ambiente MSSQL
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

**Ver [tests/README.md](tests/README.md) para documentación completa de pruebas.**

---

## 🔌 API de Conexión

### MSSQL

```python
def get_mssql_connection(
    database: str | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None
) -> pyodbc.Connection
```

**Parámetros**: Todos opcionales. Si no se proporcionan, se leen de variables de entorno.

**Variables de entorno:**
- `MSSQL_HOST` (por defecto: 'localhost')
- `MSSQL_PORT` (por defecto: 1433)
- `MSSQL_USER` (por defecto: 'sa')
- `MSSQL_PASSWORD` (por defecto: '')
- `MSSQL_DATABASE` (por defecto: 'master')

**Ejemplo:**

```python
from paquetes.mssql import select, insert, update, delete

# Consultar
registros = select('clientes', where='activo = ?', where_params=(1,), database='ventas')

# Insertar
insert('clientes', {'nombre': 'Juan', 'email': 'juan@email.com'}, database='ventas')

# Actualizar
update('clientes', {'activo': 0}, where='id = ?', where_params=(1,), database='ventas')

# Eliminar
delete('clientes', where='id = ?', where_params=(1,), database='ventas')
```

### SAP HANA

```python
def get_hana_connection(
    schema: str | None = None,
    host: str | None = None,
    port: int | None = None,
    user: str | None = None,
    password: str | None = None
) -> dbapi.Connection
```

**Parámetros**: Todos opcionales excepto credenciales si no están en variables de entorno.

**Variables de entorno:**
- `SAP_HANA_HOST` (requerido)
- `SAP_HANA_PORT` (por defecto: 30015)
- `SAP_HANA_USER` (requerido)
- `SAP_HANA_PASSWORD` (requerido)

**Nota**: SAP HANA lanzará un `ValueError` si las credenciales no están configuradas.

**Ejemplo:**

```python
from paquetes.hana import select, insert, create_table

# Consultar artículos
articulos = select(
    'OITM',
    columns=['ItemCode', 'ItemName', 'OnHand'],
    where='"OnHand" > ?',
    where_params=(0,),
    schema='SBODEMOUY'
)

# Crear tabla COLUMN store (analítica)
create_table(
    'VENTAS_ANALYTICS',
    {
        'ID': 'INTEGER',
        'FECHA': 'DATE',
        'MONTO': 'DECIMAL(18,2)'
    },
    primary_key='ID',
    table_type='COLUMN',  # COLUMN para analítica, ROW para transaccional
    schema='MI_SCHEMA'
)
```

---

## 🔍 Solución de Problemas

### Error: "Field required" o "Credenciales no configuradas"

**Causa**: Las variables de entorno no están configuradas.

**Solución**: Configura las variables de entorno o pasa credenciales directamente.

```python
# Opción 1: Variables de entorno
import os
os.environ['MSSQL_HOST'] = 'mi_servidor'
os.environ['MSSQL_USER'] = 'mi_usuario'
os.environ['MSSQL_PASSWORD'] = 'mi_password'

# Opción 2: Parámetros directos
from paquetes.mssql import get_mssql_connection
conn = get_mssql_connection(
    host='mi_servidor',
    user='mi_usuario',
    password='mi_password'
)
```

### Error: "No se puede conectar a SQL Server"

**Causas comunes:**
- Host o puerto incorrectos
- Usuario o contraseña incorrectos
- Firewall bloqueando la conexión
- Base de datos no existe

**Solución**: Verifica las credenciales y la conectividad de red.

```bash
# Probar conectividad
ping mi_servidor

# Verificar que SQL Server esté escuchando
telnet mi_servidor 1433
```

### Error: "No se puede conectar a SAP HANA"

**Causas comunes:**
- Host o puerto incorrectos (puerto típico: 30015)
- Usuario sin permisos suficientes
- HANA no está corriendo
- Red no permite conexión

**Solución**: Verifica las credenciales y que el servidor HANA esté accesible.

### Error: "ModuleNotFoundError: No module named 'mssql'"

**Causa**: El path no está configurado correctamente.

**Solución**: Asegúrate de estar en el directorio correcto o ajusta el path.

```python
import sys
sys.path.insert(0, '/ruta/a/paquetes')
from mssql import select
```

---

## 📚 Documentación de Referencia

### Módulos de Bases de Datos
- **[Módulo MSSQL](mssql/README.md)** - API completa de SQL Server (39 funciones)
- **[Módulo hana](hana/README.md)** - API completa de SAP HANA (36 funciones)
- **[Módulo sapb1sl](sapb1sl/README.md)** - Cliente REST API para SAP B1 Service Layer (14 funciones)

### Módulos de Autenticación y Directorio
- **[Módulo auth](auth/README.md)** - Sistema de autenticación con session tokens (14 funciones)
- **[Módulo ldap](ldap/README.md)** - API para LDAP/Active Directory (15 funciones)
- **[Configuración LDAP](ldap/CONFIGURATION.md)** - Guía de configuración LDAP/Active Directory

### Módulos de Facturación y Documentos Fiscales
- **[Módulo sat](sat/README.md)** - Facturación Electrónica CFDI y servicios del SAT (28 funciones + validador CSF)

### Módulos de Comunicación
- **[Módulo email](email/README.md)** - Envío de correos electrónicos con postfix local y relay SMTP (2 funciones)

### Herramientas y Aplicaciones
- **[mssql_attach_db.py](mssql_attach_db.py)** - Adjuntar bases de datos MSSQL
- **[mssql_imp_exp_tbl_vw.py](mssql_imp_exp_tbl_vw.py)** - Exportar/importar estructura de tablas y vistas
- **[auth_fastapi.py](auth_fastapi.py)** - Aplicación FastAPI con autenticación completa

### Pruebas y Ejemplos
- **[Suite de Pruebas](tests/README.md)** - Documentación de tests (61 pruebas totales)

---

## 🎓 Mejores Prácticas

### 1. Usar Variables de Entorno en Producción

```bash
# Archivo .env
MSSQL_HOST=prod-server.ejemplo.com
MSSQL_USER=app_user
MSSQL_PASSWORD=${SECRET_PASSWORD}
```

### 2. Parámetros Directos para Pruebas

```python
# test_database.py
def test_conexion():
    conn = get_mssql_connection(
        database='test_db',
        host='localhost',
        user='test_user',
        password='test_password'
    )
    assert conn is not None
```

### 3. Configuración por Entorno

```python
# config_manager.py
import os

if os.getenv('ENVIRONMENT') == 'production':
    os.environ['MSSQL_HOST'] = 'prod-server'
elif os.getenv('ENVIRONMENT') == 'staging':
    os.environ['MSSQL_HOST'] = 'staging-server'
else:
    os.environ['MSSQL_HOST'] = 'localhost'
```

---

**Versión:** 3.2.0
**Última actualización:** 2026-01-31
**Módulos totales:** 11 módulos principales + 3 herramientas genéricas
**Funciones totales:** 294+ funciones
