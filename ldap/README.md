# Módulo LDAP

Módulo completo para operaciones con LDAP y Active Directory en Python.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
  - [📖 Guía Completa de Configuración](CONFIGURATION.md)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Uso Básico](#-uso-básico)
- [API Completa](#-api-completa)
- [Ejemplos Avanzados](#-ejemplos-avanzados)
- [Derivación Automática de BASE_DN](#-derivación-automática-de-base_dn)
- [Portabilidad](#-portabilidad)
- [Troubleshooting](#-troubleshooting)

## ✨ Características

- **Conexión flexible**: Soporta LDAP y LDAPS (SSL/TLS)
- **Autenticación**: Múltiples métodos (SIMPLE, NTLM, ANONYMOUS)
- **Búsqueda avanzada**: Usuarios, grupos, OUs con filtros personalizados
- **Gestión completa de usuarios**: CRUD, habilitar/deshabilitar, cambio de contraseña
- **Gestión de grupos**: CRUD, membresías, listado de miembros
- **Gestión de OUs**: CRUD, movimiento, listado de contenido
- **Genérico y portable**: Sin valores hardcodeados, usa variables de entorno
- **Compatible con Active Directory**: Funciones específicas para AD

## 📦 Instalación

```bash
pip install ldap3
```

## ⚙️ Configuración

> 📖 **[Ver Guía Completa de Configuración](CONFIGURATION.md)** - Documentación detallada de todas las variables de entorno, derivación automática de BASE_DN, y mejores prácticas.

### Variables de Entorno

Crea un archivo `.env` con las siguientes variables:

```env
# Servidor LDAP (REQUERIDO)
LDAP_SERVER=ldap.empresa.com
LDAP_PORT=389                        # Opcional (default: 389 para LDAP, 636 para LDAPS)
LDAP_USE_SSL=false                   # Opcional (default: false, usar true para LDAPS)

# Base DN (OPCIONAL - se deriva automáticamente de LDAP_BIND_DN si no se especifica)
# LDAP_BASE_DN=DC=empresa,DC=com

# Credenciales de administrador (REQUERIDO para operaciones de modificación)
LDAP_BIND_DN=admin@empresa.com       # Formato UPN: usuario@dominio.com
# O en formato DN:
# LDAP_BIND_DN=CN=admin,DC=empresa,DC=com
LDAP_BIND_PASSWORD=password_admin

# Autenticación de usuarios (opcional)
LDAP_USER_DN_TEMPLATE=CN={username},OU=Users,DC=empresa,DC=com
LDAP_SEARCH_FILTER=(sAMAccountName={username})  # Para Active Directory
LDAP_AUTH_TYPE=SIMPLE                            # SIMPLE, NTLM, ANONYMOUS
```

#### 📌 Nota Importante sobre LDAP_BASE_DN

**LDAP_BASE_DN es OPCIONAL**. Si no se especifica, se deriva automáticamente de `LDAP_BIND_DN`:

- **Formato UPN** (`usuario@dominio.com`):
  - `admin@empresa.com` → `DC=empresa,DC=com`
  - `soporte@empresa.local` → `DC=empresa,DC=local`

- **Formato DN** (`CN=usuario,DC=dominio,DC=com`):
  - `CN=admin,OU=IT,DC=empresa,DC=com` → `DC=empresa,DC=com`

Solo especifica `LDAP_BASE_DN` si necesitas buscar en un subárbol específico:
```env
# Buscar solo en la OU de RRHH
LDAP_BASE_DN=OU=RRHH,DC=empresa,DC=com
```

### Configuración para Active Directory

```env
# Active Directory con UPN (formato recomendado)
LDAP_SERVER=dc.empresa.com
LDAP_PORT=389
LDAP_USE_SSL=false
# LDAP_BASE_DN no es necesario - se deriva de BIND_DN
LDAP_BIND_DN=administrator@empresa.com
LDAP_BIND_PASSWORD=Admin123!
LDAP_SEARCH_FILTER=(sAMAccountName={username})
LDAP_AUTH_TYPE=SIMPLE
```

```env
# Active Directory con DN completo
LDAP_SERVER=dc.empresa.com
LDAP_PORT=389
LDAP_USE_SSL=false
# LDAP_BASE_DN=DC=empresa,DC=com  # Opcional - se deriva automáticamente
LDAP_BIND_DN=CN=Administrator,CN=Users,DC=empresa,DC=com
LDAP_BIND_PASSWORD=Admin123!
LDAP_SEARCH_FILTER=(sAMAccountName={username})
LDAP_AUTH_TYPE=SIMPLE
```

### Configuración para OpenLDAP

```env
# OpenLDAP típico
LDAP_SERVER=ldap.empresa.com
LDAP_PORT=389
LDAP_USE_SSL=false
# LDAP_BASE_DN=dc=empresa,dc=com  # Opcional - se deriva automáticamente
LDAP_BIND_DN=cn=admin,dc=empresa,dc=com
LDAP_BIND_PASSWORD=admin_password
LDAP_SEARCH_FILTER=(uid={username})
LDAP_AUTH_TYPE=SIMPLE
```

## 📝 Ejemplos de Uso

El módulo incluye dos scripts de ejemplo completos en `paquetes/tests/ldap/`:

### [example_ldap_basic.py](../tests/ldap/example_ldap_basic.py)

Script interactivo para operaciones básicas de consulta:
- Prueba de conexión al servidor
- Autenticación de usuarios
- Búsqueda de usuarios y grupos
- Consultas de información

```bash
python paquetes/tests/ldap/example_ldap_basic.py
```

**Características:**
- Menú interactivo
- No requiere permisos de administrador
- Solo operaciones de lectura
- Ideal para probar la conexión

### [example_ldap_management.py](../tests/ldap/example_ldap_management.py)

Script para operaciones de administración (CRUD):
- Gestión de unidades organizativas
- Creación y modificación de usuarios
- Gestión de grupos y membresías
- Flujo completo con cleanup automático

```bash
python paquetes/tests/ldap/example_ldap_management.py
```

**Características:**
- Operaciones de modificación
- Requiere permisos de administrador
- Incluye cleanup automático
- Demostración de flujo completo

⚠️ **IMPORTANTE**: El script de gestión realiza modificaciones en el directorio LDAP. Solo ejecutar en ambiente de pruebas.

## 🚀 Uso Básico

### 1. Conexión

```python
from paquetes.ldap import get_ldap_connection, test_ldap_connection

# Probar conexión
result = test_ldap_connection()
if result['success']:
    print(f"Conectado a: {result['info']['server']}")
else:
    print(f"Error: {result['error']}")

# Obtener conexión para uso manual
conn = get_ldap_connection()
# ... usar conexión ...
conn.unbind()
```

### 2. Autenticación

```python
from paquetes.ldap import authenticate_user, verify_credentials, get_user_info

# Autenticar usuario
if authenticate_user('jperez', 'password123'):
    print("Autenticación exitosa")

# Verificar con detalle
result = verify_credentials('jperez', 'password123')
if result['valid']:
    print(f"Usuario válido: {result['dn']}")
else:
    print(f"Error: {result['error']}")

# Obtener información del usuario
user_info = get_user_info('jperez', 'password123')
if user_info:
    print(f"Nombre: {user_info.get('cn')}")
    print(f"Email: {user_info.get('mail')}")
    print(f"Grupos: {user_info.get('memberOf')}")
```

### 3. Búsqueda

```python
from paquetes.ldap import (
    search_users,
    search_groups,
    find_user_by_username,
    get_user_groups
)

# Buscar usuarios
users = search_users(filter_query='(cn=*Juan*)')
for user in users:
    print(f"{user['cn']} - {user['mail']}")

# Buscar un usuario específico
user = find_user_by_username('jperez')
if user:
    print(f"DN: {user['dn']}")
    print(f"Email: {user['mail']}")

# Obtener grupos del usuario
groups = get_user_groups('jperez')
for group_dn in groups:
    print(group_dn)

# Buscar grupos
grupos = search_groups(filter_query='(cn=Admin*)')
for grupo in grupos:
    print(f"{grupo['cn']} - {len(grupo.get('member', []))} miembros")
```

### 4. Gestión de Usuarios

```python
from paquetes.ldap import (
    create_user,
    update_user,
    disable_user,
    enable_user,
    change_user_password,
    delete_user
)

# Crear usuario
create_user(
    username='jperez',
    password='Password123!',
    first_name='Juan',
    last_name='Pérez',
    email='jperez@empresa.com',
    ou='OU=Empleados'
)

# Actualizar usuario
update_user('jperez', {
    'mail': 'juan.perez@empresa.com',
    'telephoneNumber': '+1234567890',
    'title': 'Gerente de Ventas'
})

# Deshabilitar usuario
disable_user('jperez')

# Habilitar usuario
enable_user('jperez')

# Cambiar contraseña
change_user_password('jperez', 'NewPassword123!')

# Eliminar usuario
delete_user('jperez')
```

### 5. Gestión de Grupos

```python
from paquetes.ldap import (
    create_group,
    add_user_to_group,
    remove_user_from_group,
    list_group_members,
    is_user_in_group
)

# Crear grupo
create_group(
    group_name='Desarrolladores',
    description='Equipo de desarrollo',
    ou='OU=Grupos'
)

# Agregar usuario a grupo
add_user_to_group('jperez', 'Desarrolladores')

# Verificar membresía
if is_user_in_group('jperez', 'Desarrolladores'):
    print("Usuario es miembro del grupo")

# Listar miembros del grupo
members = list_group_members('Desarrolladores', detailed=True)
for member in members:
    print(f"{member['cn']} - {member['mail']}")

# Remover usuario del grupo
remove_user_from_group('jperez', 'Desarrolladores')
```

### 6. Gestión de OUs

```python
from paquetes.ldap import (
    create_ou,
    list_ou_contents,
    move_ou,
    get_ou_tree
)

# Crear OU
create_ou('Empleados', description='Todos los empleados')
create_ou('Ventas', parent_ou='OU=Empleados', description='Equipo de ventas')

# Listar contenido de OU
contents = list_ou_contents('Empleados', object_type='user')
for item in contents:
    print(f"{item.get('cn')} - {item['dn']}")

# Obtener árbol completo de OUs
tree = get_ou_tree()
import json
print(json.dumps(tree, indent=2))
```

## 📚 API Completa

### CONNECTION (3 funciones)

| Función | Descripción |
|---------|-------------|
| `get_ldap_connection()` | Obtiene conexión a LDAP |
| `test_ldap_connection()` | Prueba la conexión y retorna info del servidor |
| `close_ldap_connection()` | Cierra conexión de forma segura |

### AUTH (3 funciones)

| Función | Descripción |
|---------|-------------|
| `authenticate_user()` | Autentica usuario contra LDAP |
| `get_user_info()` | Autentica y retorna información del usuario |
| `verify_credentials()` | Verifica credenciales con detalle |

### SEARCH (8 funciones)

| Función | Descripción |
|---------|-------------|
| `search_users()` | Busca usuarios con filtro personalizado |
| `search_groups()` | Busca grupos con filtro personalizado |
| `search_organizational_units()` | Busca OUs con filtro personalizado |
| `search_custom()` | Búsqueda personalizada con cualquier filtro |
| `find_user_by_username()` | Busca usuario específico por username |
| `find_group_by_name()` | Busca grupo específico por nombre |
| `get_user_groups()` | Obtiene lista de grupos de un usuario |
| `get_group_members()` | Obtiene lista de miembros de un grupo |

### USERS (8 funciones)

| Función | Descripción |
|---------|-------------|
| `create_user()` | Crea nuevo usuario |
| `update_user()` | Actualiza atributos de usuario |
| `delete_user()` | Elimina usuario (irreversible) |
| `disable_user()` | Deshabilita cuenta sin eliminar |
| `enable_user()` | Habilita cuenta deshabilitada |
| `change_user_password()` | Cambia contraseña de usuario |
| `move_user()` | Mueve usuario a otra OU |
| `user_exists()` | Verifica si usuario existe |

### GROUPS (8 funciones)

| Función | Descripción |
|---------|-------------|
| `create_group()` | Crea nuevo grupo |
| `delete_group()` | Elimina grupo (irreversible) |
| `add_user_to_group()` | Agrega usuario a grupo |
| `remove_user_from_group()` | Remueve usuario de grupo |
| `is_user_in_group()` | Verifica membresía de usuario |
| `list_group_members()` | Lista miembros de un grupo |
| `update_group()` | Actualiza atributos de grupo |
| `group_exists()` | Verifica si grupo existe |

### OUS (7 funciones)

| Función | Descripción |
|---------|-------------|
| `create_ou()` | Crea nueva OU |
| `delete_ou()` | Elimina OU (irreversible) |
| `update_ou()` | Actualiza atributos de OU |
| `move_ou()` | Mueve OU a nueva ubicación |
| `list_ou_contents()` | Lista contenido de OU |
| `ou_exists()` | Verifica si OU existe |
| `get_ou_tree()` | Obtiene árbol jerárquico de OUs |

**Total: 45 funciones**

## 🔧 Ejemplos Avanzados

### Búsqueda Avanzada con Filtros

```python
from paquetes.ldap import search_custom

# Buscar usuarios activos creados recientemente
users = search_custom(
    filter_query='(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(whenCreated>=20240101000000.0Z))',
    attributes=['cn', 'mail', 'whenCreated']
)

# Buscar grupos de seguridad global
groups = search_custom(
    filter_query='(&(objectClass=group)(groupType:1.2.840.113556.1.4.803:=2147483648))',
    attributes=['cn', 'member']
)
```

### Gestión Masiva de Usuarios

```python
from paquetes.ldap import create_user, add_user_to_group

# Crear múltiples usuarios
usuarios_nuevos = [
    {'username': 'jperez', 'first_name': 'Juan', 'last_name': 'Pérez', 'email': 'jperez@empresa.com'},
    {'username': 'mlopez', 'first_name': 'María', 'last_name': 'López', 'email': 'mlopez@empresa.com'},
    {'username': 'cgarcia', 'first_name': 'Carlos', 'last_name': 'García', 'email': 'cgarcia@empresa.com'}
]

for user_data in usuarios_nuevos:
    try:
        create_user(
            username=user_data['username'],
            password='Temporal123!',
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            ou='OU=Empleados'
        )

        # Agregar a grupo por defecto
        add_user_to_group(user_data['username'], 'Empleados')

        print(f"✓ Usuario {user_data['username']} creado")
    except Exception as e:
        print(f"✗ Error creando {user_data['username']}: {e}")
```

### Auditoría de Grupos

```python
from paquetes.ldap import search_groups, list_group_members

# Obtener todos los grupos
grupos = search_groups()

print("=== Auditoría de Grupos ===\n")
for grupo in grupos:
    nombre = grupo.get('cn', 'Sin nombre')
    descripcion = grupo.get('description', 'Sin descripción')

    # Obtener miembros detallados
    miembros = list_group_members(nombre, detailed=True)

    print(f"Grupo: {nombre}")
    print(f"Descripción: {descripcion}")
    print(f"Miembros: {len(miembros)}")

    if miembros:
        print("  Usuarios:")
        for miembro in miembros[:5]:  # Mostrar solo los primeros 5
            print(f"    - {miembro.get('cn')} ({miembro.get('mail')})")

        if len(miembros) > 5:
            print(f"    ... y {len(miembros) - 5} más")

    print()
```

### Sincronización de Estructura de OUs

```python
from paquetes.ldap import create_ou, ou_exists

# Estructura deseada
estructura_ous = {
    'Empleados': {
        'description': 'Todos los empleados',
        'children': {
            'Ventas': {'description': 'Equipo de ventas'},
            'Marketing': {'description': 'Equipo de marketing'},
            'IT': {
                'description': 'Tecnología',
                'children': {
                    'Desarrollo': {'description': 'Desarrolladores'},
                    'Soporte': {'description': 'Soporte técnico'}
                }
            }
        }
    }
}

def crear_estructura(estructura, parent_ou=None):
    """Crea estructura de OUs recursivamente."""
    for ou_name, config in estructura.items():
        if not ou_exists(ou_name, parent_ou=parent_ou):
            create_ou(
                ou_name=ou_name,
                description=config.get('description'),
                parent_ou=parent_ou
            )
            print(f"✓ OU creada: {ou_name}")
        else:
            print(f"○ OU ya existe: {ou_name}")

        # Crear OUs hijas
        if 'children' in config:
            current_ou = f'OU={ou_name}'
            if parent_ou:
                current_ou = f'{current_ou},{parent_ou}'
            crear_estructura(config['children'], current_ou)

# Ejecutar
crear_estructura(estructura_ous)
```

### Migración de Usuarios Entre OUs

```python
from paquetes.ldap import list_ou_contents, move_user

# Mover todos los usuarios de una OU a otra
usuarios_origen = list_ou_contents('Temporal', object_type='user')

print(f"Moviendo {len(usuarios_origen)} usuarios de Temporal a Empleados...\n")

for usuario in usuarios_origen:
    username = usuario.get('sAMAccountName')
    if username:
        try:
            move_user(username, 'OU=Empleados')
            print(f"✓ {username} movido")
        except Exception as e:
            print(f"✗ Error moviendo {username}: {e}")
```

## 🔄 Portabilidad

Este módulo es **completamente genérico** y puede copiarse a cualquier proyecto Python:

### Características de Portabilidad

✅ **Sin dependencias internas**: Solo requiere `ldap3`
✅ **Sin valores hardcodeados**: Todo configurable por variables de entorno o parámetros
✅ **Independiente de config.py**: No depende de configuración del proyecto
✅ **Funciona standalone**: Puede usarse como paquete independiente

### Cómo Usar en Otro Proyecto

```bash
# 1. Copiar carpeta completa
cp -r paquetes/ldap /otro_proyecto/

# 2. Instalar dependencias
pip install ldap3

# 3. Configurar variables de entorno
# Crear archivo .env con las variables necesarias

# 4. Usar
from ldap import authenticate_user, search_users
```

## 🔧 Derivación Automática de BASE_DN

El módulo LDAP incluye una funcionalidad avanzada que **deriva automáticamente** el `LDAP_BASE_DN` del `LDAP_BIND_DN`, haciendo que la configuración sea más simple y menos propensa a errores.

### ¿Cómo Funciona?

Si no especificas `LDAP_BASE_DN` en las variables de entorno, el módulo lo deriva automáticamente del `LDAP_BIND_DN`:

#### Desde formato UPN (User Principal Name)

```env
LDAP_BIND_DN=soporte@empresa.local
# Se deriva automáticamente: LDAP_BASE_DN=DC=empresa,DC=local

LDAP_BIND_DN=admin@empresa.com
# Se deriva automáticamente: LDAP_BASE_DN=DC=empresa,DC=com

LDAP_BIND_DN=usuario@sub.dominio.local
# Se deriva automáticamente: LDAP_BASE_DN=DC=sub,DC=dominio,DC=local
```

#### Desde formato DN (Distinguished Name)

```env
LDAP_BIND_DN=CN=admin,OU=IT,DC=empresa,DC=com
# Se deriva automáticamente: LDAP_BASE_DN=DC=empresa,DC=com

LDAP_BIND_DN=CN=soporte,OU=IT,DC=empresa,DC=local
# Se deriva automáticamente: LDAP_BASE_DN=DC=empresa,DC=local
```

### Configuración Mínima Requerida

Con esta funcionalidad, solo necesitas especificar:

```env
# Configuración mínima para Active Directory
LDAP_SERVER=ldap.empresa.local
LDAP_BIND_DN=admin@empresa.com
LDAP_BIND_PASSWORD=password123
```

**¡Eso es todo!** No necesitas especificar `LDAP_PORT`, `LDAP_USE_SSL`, ni `LDAP_BASE_DN`.

### Ventajas

1. **Configuración más simple**: Menos variables de entorno requeridas
2. **Menos errores**: No hay riesgo de inconsistencia entre BIND_DN y BASE_DN
3. **Más legible**: El formato UPN es más fácil de leer y mantener
4. **Compatible**: Sigue funcionando si especificas BASE_DN explícitamente

### ¿Cuándo Especificar BASE_DN Explícitamente?

Especifica `LDAP_BASE_DN` cuando necesites buscar en un **subárbol específico** del directorio:

```env
# Buscar solo dentro de la OU de RRHH
LDAP_BASE_DN=OU=RRHH,DC=empresa,DC=com

# Buscar solo dentro de una sucursal específica
LDAP_BASE_DN=OU=Sucursal_Norte,OU=Sucursales,DC=empresa,DC=com
```

### Ejemplo Comparativo

#### Antes (configuración tradicional):
```env
LDAP_SERVER=ldap.empresa.local
LDAP_PORT=389
LDAP_USE_SSL=false
LDAP_BASE_DN=DC=empresa,DC=local              # Redundante
LDAP_BIND_DN=soporte@empresa.local       # Ya contiene el dominio
LDAP_BIND_PASSWORD=MiPasswordSeguro
```

#### Ahora (configuración simplificada):
```env
LDAP_SERVER=ldap.empresa.local
LDAP_BIND_DN=soporte@empresa.local       # BASE_DN se deriva automáticamente
LDAP_BIND_PASSWORD=MiPasswordSeguro
```

### Validación

Para verificar qué BASE_DN se está usando:

```python
from paquetes.ldap import test_ldap_connection

result = test_ldap_connection()
if result['success']:
    print(f"Naming Contexts: {result['info']['naming_contexts']}")
    # El primer naming context es el BASE_DN derivado
```

## 🔍 Troubleshooting

### Error: "Can't contact LDAP server"

```python
# Verificar conectividad
from paquetes.ldap import test_ldap_connection

result = test_ldap_connection()
print(result)

# Posibles soluciones:
# 1. Verificar que LDAP_SERVER sea correcto
# 2. Verificar que el puerto esté abierto (389 o 636)
# 3. Si usa SSL, cambiar LDAP_USE_SSL=true
```

### Error: "Invalid credentials"

```python
# Verificar credenciales de administrador
import os
print(f"LDAP_BIND_DN: {os.getenv('LDAP_BIND_DN')}")
print(f"LDAP_BASE_DN: {os.getenv('LDAP_BASE_DN', 'Se derivará automáticamente')}")

# Probar autenticación simple
from paquetes.ldap import verify_credentials
result = verify_credentials('usuario', 'password')
print(result)

# Si el BASE_DN no se está derivando correctamente, especifícalo:
# export LDAP_BASE_DN=DC=empresa,DC=com
```

### Error al crear usuarios (Active Directory)

```python
# Verificar permisos del usuario administrador
# El usuario debe tener permisos para crear objetos en el contenedor

# Verificar que la contraseña cumpla políticas de AD
# - Mínimo 8 caracteres
# - Mayúsculas, minúsculas, números y símbolos
# - No contener el nombre de usuario

# Ejemplo de contraseña válida para AD:
password = "Temp2024!"
```

### Problemas con SSL/TLS

```python
# Si usa LDAPS pero hay problemas con certificados:

# Opción 1: Configurar para aceptar certificados autofirmados
from ldap3 import Tls
import ssl

tls_configuration = Tls(validate=ssl.CERT_NONE)

# Usar con get_ldap_connection requiere modificación del código
# o configurar a nivel de sistema
```

### Búsquedas que no retornan resultados

```python
# Verificar el filtro LDAP
from paquetes.ldap import search_custom, test_ldap_connection

# Buscar TODO para verificar conectividad
all_objects = search_custom('(objectClass=*)', limit=10)
print(f"Encontrados: {len(all_objects)} objetos")

# Verificar el base_dn que se está usando
import os
print(f"LDAP_BASE_DN especificado: {os.getenv('LDAP_BASE_DN', 'No especificado')}")

# Ver qué BASE_DN se está usando (derivado o especificado)
result = test_ldap_connection()
if result['success']:
    print(f"Naming contexts disponibles: {result['info']['naming_contexts']}")

# Si necesitas buscar en un OU específico, especifica BASE_DN:
# export LDAP_BASE_DN=OU=Usuarios,DC=empresa,DC=com
```

## 📝 Notas Importantes

### Permisos

- **Lectura/Búsqueda**: No requiere permisos especiales, puede usar bind anónimo o usuario de solo lectura
- **Autenticación**: Cada usuario autentica con sus propias credenciales
- **Modificación** (crear/actualizar/eliminar): Requiere credenciales de administrador en `LDAP_BIND_DN`

### Active Directory vs OpenLDAP

| Característica | Active Directory | OpenLDAP |
|----------------|------------------|----------|
| Atributo usuario | `sAMAccountName` | `uid` |
| Cambio contraseña | `unicodePwd` (UTF-16-LE) | `userPassword` |
| Deshabilitar cuenta | `userAccountControl=514` | `shadowExpire` |
| Tipo de grupo | `groupType` | `objectClass=groupOfNames` |

### Seguridad

⚠️ **Recomendaciones**:
- Usar LDAPS (SSL/TLS) en producción
- No almacenar contraseñas en código
- Usar variables de entorno o gestores de secretos
- Aplicar principio de mínimo privilegio para cuenta de administrador
- Auditar operaciones de modificación

## 🌐 Referencias

- [ldap3 Documentation](https://ldap3.readthedocs.io/)
- [LDAP RFC 4511](https://tools.ietf.org/html/rfc4511)
- [Active Directory Schema](https://docs.microsoft.com/en-us/windows/win32/adschema/active-directory-schema)

---

**Versión:** 1.0.0
**Última actualización:** 2026-01-31
