# SAP Business One Service Layer - Cliente REST API

> ⚠️ **MÓDULO GENÉRICO**: Este módulo NO tiene valores por defecto hardcodeados. El usuario debe proporcionar TODAS las credenciales en el archivo `.env` o por parámetros.

Cliente completo para SAP Business One Service Layer (API REST).

## 📋 Características

- ✅ **Autenticación automática**: Login, logout y gestión de sesiones
- ✅ **CRUD completo**: GET, POST, PATCH, DELETE
- ✅ **Queries OData**: $filter, $select, $expand, $orderby, $top, $skip, $inlinecount
- ✅ **Total count**: Soporte para `inlinecount=True` (obtener total de registros)
- ✅ **Paginación configurable**: `max_page_size=0` (default) obtiene todos los registros
- ✅ **Genérico**: Sin hardcodeo, portable a cualquier proyecto
- ✅ **Caché de sesión**: Reutiliza sesión activa automáticamente
- ✅ **Type hints**: Documentación completa con tipos

## 📦 Estructura

```
sapb1sl/
├── __init__.py          # Exporta todas las funciones (14 funciones)
├── sl_auth.py           # Autenticación y sesiones (4 funciones)
├── sl_crud.py           # Operaciones CRUD (6 funciones)
├── sl_queries.py        # Queries OData (5 funciones)
└── README.md            # Este archivo
```

## 🔧 Instalación

### Dependencias

```bash
pip install requests urllib3
```

### Variables de Entorno

Configurar en `/infraestructura/.env`:

```env
# SAP Business One Service Layer
SAP_B1_SERVICE_LAYER_URL=https://sap.empresa.local:50000/b1s/v1
SAP_B1_USER=manager
SAP_B1_PASSWORD=tu_password

# Opcional: Base de datos de la compañía
SAP_B1_COMPANY_DB=SBODEMOUY
```

## 🚀 Uso Rápido

### Autenticación

```python
from paquetes.sapb1sl import login, logout, get_session

# Login manual
session = login()
print(session['session_id'])

# Obtener sesión (recomendado - gestión automática)
session = get_session()

# Logout
logout()
```

### Consultar Entidades (GET)

```python
from paquetes.sapb1sl import get_entity, query_entities

# Obtener un item por código
item = get_entity('Items', 'A00001')
print(item['ItemName'])

# Con selección de campos
item = get_entity('Items', 'A00001', select='ItemCode,ItemName,Price')

# Consultar múltiples entidades (sin límite de página - trae todos)
items = query_entities(
    'Items',
    filter="ItemType eq 'itItems' and Valid eq 'tYES'",
    select='ItemCode,ItemName,Price',
    orderby='ItemName asc'
)

for item in items:
    print(f"{item['ItemCode']}: {item['ItemName']}")

# Con límite de página personalizado (ej: 100 registros por página)
items_paginados = query_entities(
    'Items',
    filter="Valid eq 'tYES'",
    max_page_size=100
)

# Con inlinecount para obtener el total de registros
resultado = query_entities(
    'BusinessPartners',
    filter="CardType eq 'S'",  # Proveedores
    select='CardCode,CardName,City,EmailAddress',
    inlinecount=True  # Incluir total count
)

print(f"Total proveedores: {resultado['count']}")
print(f"Obtenidos: {len(resultado['value'])}")

for proveedor in resultado['value'][:5]:  # Primeros 5
    print(f"{proveedor['CardCode']}: {proveedor['CardName']}")
```

**Notas:**
- **Paginación:** Por defecto, `max_page_size=0` retorna **todos** los registros sin límite.
- **Inlinecount:** Cuando `inlinecount=True`, retorna `{'value': [...], 'count': total}` en lugar de solo la lista.

### Crear Entidades (POST)

```python
from paquetes.sapb1sl import create_entity

# Crear nuevo item
item_data = {
    'ItemCode': 'A00001',
    'ItemName': 'Producto Nuevo',
    'ItemType': 'itItems',
    'ItemsGroupCode': 100
}

result = create_entity('Items', item_data)
print(f"Item creado: {result['ItemCode']}")
```

### Actualizar Entidades (PATCH)

```python
from paquetes.sapb1sl import update_entity

# Actualizar precio de item
update_entity('Items', 'A00001', {'Price': 150.00})

# Actualizar múltiples campos
update_entity('Items', 'A00001', {
    'Price': 150.00,
    'ItemName': 'Producto Actualizado'
})
```

### Eliminar Entidades (DELETE)

```python
from paquetes.sapb1sl import delete_entity

# Eliminar item
delete_entity('Items', 'A00001')
```

## 🔍 Queries Avanzadas con OData

### Usando Query Helpers

```python
from paquetes.sapb1sl import execute_query

# Query completa con helpers (obtiene todos los registros)
items = execute_query(
    entity_name='Items',
    conditions={'ItemType': 'itItems', 'Valid': 'tYES'},
    select_fields=['ItemCode', 'ItemName', 'Price'],
    order_by={'ItemName': 'asc'}
)

# Con expansión de relaciones (sin límite de página)
partners = execute_query(
    entity_name='BusinessPartners',
    conditions={'CardType': 'cSupplier'},
    select_fields=['CardCode', 'CardName'],
    expand_relations=['BusinessPartnerAddresses', 'ContactEmployees']
)

# Con límite de página personalizado
items_paginados = execute_query(
    entity_name='Items',
    conditions={'Valid': 'tYES'},
    max_page_size=100  # Máximo 100 registros
)
```

### Filtros Manuales OData

```python
from paquetes.sapb1sl import query_entities

# Filtro complejo
items = query_entities(
    'Items',
    filter="ItemType eq 'itItems' and Price gt 100 and Price lt 500"
)

# Con operadores lógicos
items = query_entities(
    'Items',
    filter="(ItemType eq 'itItems' or ItemType eq 'itLabor') and Valid eq 'tYES'"
)

# Filtro con like (contains)
items = query_entities(
    'Items',
    filter="contains(ItemName, 'Motor')"
)

# Filtro con startswith
items = query_entities(
    'Items',
    filter="startswith(ItemCode, 'A')"
)
```

### Paginación

El módulo soporta dos formas de controlar la paginación:

**1. Paginación del Service Layer (Recomendado)**

Por defecto, `max_page_size=0` obtiene **todos** los registros sin límite:

```python
from paquetes.sapb1sl import query_entities

# Obtener TODOS los registros (sin límite)
all_items = query_entities('Items', filter="Valid eq 'tYES'")
print(f"Total items: {len(all_items)}")  # Podría ser 10,000+

# Con límite de página del Service Layer
items = query_entities('Items', max_page_size=100)  # Máximo 100 por llamada
```

**2. Paginación Manual con $top y $skip**

Para paginación manual cliente-side:

```python
# Primera página (0-99)
page1 = query_entities('Items', top=100, skip=0)

# Segunda página (100-199)
page2 = query_entities('Items', top=100, skip=100)

# Tercera página (200-299)
page3 = query_entities('Items', top=100, skip=200)
```

**Recomendación:** Usa `max_page_size=0` (default) para obtener todos los registros en una sola llamada, a menos que trabajes con datasets muy grandes (>10,000 registros) donde es mejor usar paginación manual.

## 📚 API Completa

### Autenticación (sl_auth.py)

| Función | Descripción |
|---------|-------------|
| `login()` | Inicia sesión en Service Layer |
| `logout()` | Cierra sesión |
| `get_session()` | Obtiene sesión activa (recomendado) |
| `is_session_active()` | Verifica si hay sesión activa |

### CRUD (sl_crud.py)

| Función | Descripción | Método HTTP |
|---------|-------------|-------------|
| `get_entity()` | Obtiene entidad por clave | GET |
| `query_entities()` | Consulta múltiples entidades | GET |
| `create_entity()` | Crea nueva entidad | POST |
| `update_entity()` | Actualiza entidad existente | PATCH |
| `delete_entity()` | Elimina entidad | DELETE |
| `batch_request()` | Operaciones en batch (WIP) | POST $batch |

### Queries OData (sl_queries.py)

| Función | Descripción |
|---------|-------------|
| `build_filter()` | Construye string de filtro |
| `build_select()` | Construye string de selección |
| `build_expand()` | Construye string de expansión |
| `build_orderby()` | Construye string de ordenamiento |
| `execute_query()` | Query completa con helpers |

## 🎯 Ejemplos Prácticos

### Sincronizar Proveedores con Total Count

```python
from paquetes.sapb1sl import query_entities

# Obtener TODOS los proveedores con total count
resultado = query_entities(
    'BusinessPartners',
    filter="CardType eq 'S'",  # 'S' = Supplier (Proveedor)
    select='CardCode,CardName,Phone1,EmailAddress,City,UpdateDate',
    orderby='CardCode asc',
    inlinecount=True  # Incluir total count
)

proveedores = resultado['value']
total = resultado['count']

print(f"Total de proveedores en SAP: {total}")
print(f"Proveedores sincronizados: {len(proveedores)}")

for prov in proveedores:
    print(f"{prov['CardCode']}: {prov['CardName']} - {prov.get('City', 'N/A')}")
```

### Proveedores Solo Activos

```python
from paquetes.sapb1sl import execute_query

# Usando helper con múltiples condiciones
resultado = execute_query(
    entity_name='BusinessPartners',
    conditions={
        'CardType': 'S',      # Proveedores
        'Valid': 'tYES'       # Solo activos
    },
    select_fields=['CardCode', 'CardName', 'EmailAddress', 'UpdateDate'],
    inlinecount=True
)

print(f"Proveedores activos: {resultado['count']}")
```

### Crear Orden de Compra

```python
from paquetes.sapb1sl import create_entity

orden_data = {
    'CardCode': 'P00001',
    'DocDate': '2026-01-24',
    'DocumentLines': [
        {
            'ItemCode': 'A00001',
            'Quantity': 10,
            'Price': 150.00
        },
        {
            'ItemCode': 'A00002',
            'Quantity': 5,
            'Price': 200.00
        }
    ]
}

orden = create_entity('PurchaseOrders', orden_data)
print(f"Orden creada: {orden['DocNum']}")
```

### Consultar Stock de Items

```python
from paquetes.sapb1sl import execute_query

items_con_stock = execute_query(
    entity_name='Items',
    conditions={'Valid': 'tYES'},
    select_fields=['ItemCode', 'ItemName', 'QuantityOnStock', 'Price'],
    order_by={'QuantityOnStock': 'desc'},
    top=50
)

for item in items_con_stock:
    print(f"{item['ItemCode']}: Stock={item['QuantityOnStock']}")
```

## 🔐 Seguridad

### Certificados SSL

El módulo deshabilita verificación SSL por defecto (Service Layer usa certificados auto-firmados). Para producción con certificados válidos:

```python
# Modificar en sl_auth.py y sl_crud.py:
# verify=False  →  verify=True
```

### Credenciales

**NUNCA** hardcodear credenciales en el código:

```python
# ❌ MAL
session = login(url='https://...', user='manager', password='pass123')

# ✅ BIEN - Usar variables de entorno
session = login()  # Lee de .env automáticamente
```

## 🔧 Detalles Técnicos

### Control de Paginación

El módulo controla la paginación mediante el header HTTP `Prefer`:

```
Prefer: odata.maxpagesize=0
```

**Valores:**
- `0` (default): Sin límite, retorna todos los registros
- `>0`: Límite específico de registros por página

Este header se incluye automáticamente en todas las peticiones GET (`get_entity`, `query_entities`, `execute_query`).

**Ejemplo de uso interno:**
```python
headers = {
    'Prefer': 'odata.maxpagesize=0'  # Todos los registros
}
response = requests.get(url, headers=headers, cookies=cookies)
```

## ⚠️ Limitaciones Conocidas

1. **batch_request()**: No implementado aún (usar operaciones individuales)
2. **SSL**: Certificados auto-firmados requieren `verify=False`
3. **Timeout de sesión**: 30 minutos (Service Layer default)
4. **Datasets muy grandes**: Con `max_page_size=0` y >50,000 registros, considerar paginación manual

## 🔗 Recursos

- [SAP B1 Service Layer Reference](https://help.sap.com/doc/0d2533ad95ba4ad7a702e83570a21c32/10.0/en-US/ServiceLayerReference.html)
- [OData v4 Protocol](https://www.odata.org/documentation/)
- [SAP B1 Service Layer Guide](https://blogs.sap.com/2017/05/09/getting-started-with-the-sap-business-one-service-layer/)

## 📝 Changelog

### v1.2.0 (2026-01-24)
- ✅ Soporte para `$inlinecount=allpages` (obtener total count)
- ✅ Parámetro `inlinecount` en `query_entities` y `execute_query`
- ✅ Retorno flexible: lista (default) o dict con value+count (inlinecount=True)
- ✅ Ejemplo completo de consulta de proveedores
- ✅ Documentación actualizada con ejemplos de inlinecount

### v1.1.0 (2026-01-24)
- ✅ Control de paginación con header `Prefer: odata.maxpagesize`
- ✅ Parámetro `max_page_size` en `query_entities`, `get_entity` y `execute_query`
- ✅ Por defecto `max_page_size=0` (sin límite, obtiene todos los registros)
- ✅ Documentación actualizada con ejemplos de paginación

### v1.0.0 (2026-01-24)
- ✅ Autenticación con login/logout
- ✅ CRUD completo (GET, POST, PATCH, DELETE)
- ✅ Queries OData con filtros, selección, ordenamiento
- ✅ Gestión automática de sesiones
- ✅ Helpers para construcción de queries

---

**Versión:** 1.2.0
**Última actualización:** 2026-01-31
