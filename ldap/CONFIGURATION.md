# Configuración LDAP - Guía Completa

Documentación detallada de todas las variables de entorno para el módulo LDAP.

## 📋 Índice

- [Variables Requeridas](#variables-requeridas)
- [Variables Opcionales](#variables-opcionales)
- [Derivación Automática de BASE_DN](#derivación-automática-de-base_dn)
- [Ejemplos de Configuración](#ejemplos-de-configuración)
- [Mejores Prácticas](#mejores-prácticas)

---

## Variables Requeridas

### LDAP_SERVER

**Descripción**: Dirección del servidor LDAP/Active Directory.

**Tipo**: String (hostname o IP)

**Requerido**: ✅ SÍ

**Ejemplos**:
```env
LDAP_SERVER=ldap.empresa.com
LDAP_SERVER=dc.empresa.local
LDAP_SERVER=10.0.0.10
```

---

### LDAP_BIND_DN

**Descripción**: Credenciales para autenticación en el servidor LDAP. Puede estar en formato UPN o DN completo.

**Tipo**: String

**Requerido**: ✅ SÍ (para operaciones de modificación)

**Formatos Soportados**:

1. **UPN (User Principal Name)** - Recomendado para Active Directory:
   ```env
   LDAP_BIND_DN=admin@empresa.com
   LDAP_BIND_DN=soporte@empresa.local
   ```

2. **DN (Distinguished Name)** - Compatible con OpenLDAP y AD:
   ```env
   LDAP_BIND_DN=CN=admin,DC=empresa,DC=com
   LDAP_BIND_DN=CN=soporte,OU=IT,DC=empresa,DC=local
   LDAP_BIND_DN=cn=admin,dc=empresa,dc=com
   ```

**Nota**: Si usas formato UPN o DN con componentes DC, `LDAP_BASE_DN` se derivará automáticamente.

---

### LDAP_BIND_PASSWORD

**Descripción**: Contraseña para las credenciales especificadas en `LDAP_BIND_DN`.

**Tipo**: String

**Requerido**: ✅ SÍ (para operaciones de modificación)

**Ejemplo**:
```env
LDAP_BIND_PASSWORD=MiPassword123!
```

**Seguridad**:
- Nunca comitear al repositorio
- Usar gestores de secretos en producción
- Rotar periódicamente

---

## Variables Opcionales

### LDAP_BASE_DN

**Descripción**: Punto de inicio para búsquedas en el directorio LDAP.

**Tipo**: String (Distinguished Name)

**Requerido**: ❌ NO (se deriva automáticamente de `LDAP_BIND_DN`)

**Default**: Se deriva de `LDAP_BIND_DN`

**¿Cuándo especificar?**:
- Para buscar solo en un subárbol específico del directorio
- Para optimizar búsquedas limitándolas a una OU específica

**Ejemplos**:
```env
# Dominio completo
LDAP_BASE_DN=DC=empresa,DC=com

# Solo una OU específica
LDAP_BASE_DN=OU=RRHH,DC=empresa,DC=com

# Subárbol más profundo
LDAP_BASE_DN=OU=Desarrolladores,OU=IT,DC=empresa,DC=local
```

**Derivación Automática**:
Si no se especifica, se deriva así:

| LDAP_BIND_DN | LDAP_BASE_DN Derivado |
|--------------|----------------------|
| `admin@empresa.com` | `DC=empresa,DC=com` |
| `soporte@empresa.local` | `DC=empresa,DC=local` |
| `user@sub.dominio.com` | `DC=sub,DC=dominio,DC=com` |
| `CN=admin,OU=IT,DC=empresa,DC=com` | `DC=empresa,DC=com` |

---

### LDAP_PORT

**Descripción**: Puerto del servidor LDAP.

**Tipo**: Integer

**Requerido**: ❌ NO

**Default**:
- `389` para LDAP sin cifrado
- `636` para LDAPS (con SSL/TLS)

**Ejemplos**:
```env
LDAP_PORT=389        # LDAP estándar
LDAP_PORT=636        # LDAPS (SSL/TLS)
LDAP_PORT=3268       # Global Catalog (AD)
LDAP_PORT=3269       # Global Catalog SSL (AD)
```

---

### LDAP_USE_SSL

**Descripción**: Habilita conexión cifrada mediante SSL/TLS (LDAPS).

**Tipo**: Boolean (string)

**Requerido**: ❌ NO

**Default**: `false`

**Valores Válidos**: `true`, `false` (case insensitive)

**Ejemplos**:
```env
LDAP_USE_SSL=false    # LDAP sin cifrado (puerto 389)
LDAP_USE_SSL=true     # LDAPS con SSL/TLS (puerto 636)
```

**Recomendación**: Usar `true` en producción para seguridad.

---

### LDAP_AUTH_TYPE

**Descripción**: Método de autenticación LDAP.

**Tipo**: String (enum)

**Requerido**: ❌ NO

**Default**: `SIMPLE`

**Valores Válidos**:
- `SIMPLE`: Autenticación simple con usuario/contraseña
- `NTLM`: Autenticación Windows NTLM (Active Directory)
- `ANONYMOUS`: Sin autenticación (solo lectura pública)

**Ejemplos**:
```env
LDAP_AUTH_TYPE=SIMPLE      # Más común
LDAP_AUTH_TYPE=NTLM        # Para entornos Windows específicos
LDAP_AUTH_TYPE=ANONYMOUS   # Solo lectura sin credenciales
```

---

### LDAP_USER_DN_TEMPLATE

**Descripción**: Plantilla para construir el DN de usuarios al autenticar.

**Tipo**: String (template con `{username}`)

**Requerido**: ❌ NO

**Uso**: Para autenticación de usuarios cuando conoces la estructura DN exacta.

**Ejemplos**:
```env
# Active Directory
LDAP_USER_DN_TEMPLATE=CN={username},OU=Users,DC=empresa,DC=com

# OpenLDAP
LDAP_USER_DN_TEMPLATE=uid={username},ou=people,dc=empresa,dc=com

# Estructura personalizada
LDAP_USER_DN_TEMPLATE=CN={username},OU=Empleados,OU=RRHH,DC=empresa,DC=com
```

**Nota**: Si no se especifica, se usa `LDAP_SEARCH_FILTER` para encontrar el usuario.

---

### LDAP_SEARCH_FILTER

**Descripción**: Filtro LDAP para buscar usuarios al autenticar.

**Tipo**: String (filtro LDAP con `{username}`)

**Requerido**: ❌ NO

**Default**: `(sAMAccountName={username})`

**Uso**: Se usa cuando no tienes `LDAP_USER_DN_TEMPLATE` o como filtro para búsquedas.

**Ejemplos**:
```env
# Active Directory (default)
LDAP_SEARCH_FILTER=(sAMAccountName={username})

# Active Directory por email
LDAP_SEARCH_FILTER=(mail={username})

# Active Directory por UPN
LDAP_SEARCH_FILTER=(userPrincipalName={username})

# OpenLDAP
LDAP_SEARCH_FILTER=(uid={username})

# Múltiples atributos
LDAP_SEARCH_FILTER=(|(sAMAccountName={username})(mail={username}))
```

---

## Derivación Automática de BASE_DN

El módulo LDAP incluye lógica inteligente para derivar `LDAP_BASE_DN` automáticamente del `LDAP_BIND_DN`.

### Algoritmo de Derivación

1. **Si `LDAP_BASE_DN` está especificado**: Se usa el valor especificado
2. **Si `LDAP_BIND_DN` tiene formato UPN** (`usuario@dominio.com`):
   - Extrae el dominio después del `@`
   - Convierte cada parte del dominio a componente DC
   - Ejemplo: `admin@empresa.com` → `DC=empresa,DC=com`
3. **Si `LDAP_BIND_DN` tiene formato DN** con componentes DC:
   - Extrae solo las partes que empiezan con `DC=`
   - Ejemplo: `CN=admin,OU=IT,DC=empresa,DC=com` → `DC=empresa,DC=com`

### Ejemplos de Derivación

```python
# Ejemplo 1: UPN simple
LDAP_BIND_DN = "admin@empresa.com"
# Derivado: DC=empresa,DC=com

# Ejemplo 2: UPN con subdominio
LDAP_BIND_DN = "usuario@sub.empresa.local"
# Derivado: DC=sub,DC=empresa,DC=local

# Ejemplo 3: DN con OU
LDAP_BIND_DN = "CN=soporte,OU=IT,DC=empresa,DC=local"
# Derivado: DC=empresa,DC=local

# Ejemplo 4: DN profundo
LDAP_BIND_DN = "CN=admin,OU=Admins,OU=IT,OU=Departamentos,DC=empresa,DC=com"
# Derivado: DC=empresa,DC=com
```

### Código Interno

```python
# Derivación desde UPN
if '@' in ldap_bind_dn:
    domain = ldap_bind_dn.split('@')[1]
    ldap_base_dn = ','.join([f'DC={part}' for part in domain.split('.')])

# Derivación desde DN
elif 'DC=' in ldap_bind_dn.upper():
    parts = ldap_bind_dn.split(',')
    dc_parts = [part.strip() for part in parts if part.strip().upper().startswith('DC=')]
    ldap_base_dn = ','.join(dc_parts)
```

---

## Ejemplos de Configuración

### Configuración Mínima (Active Directory)

```env
# Solo las 3 variables esenciales
LDAP_SERVER=dc.empresa.com
LDAP_BIND_DN=admin@empresa.com
LDAP_BIND_PASSWORD=Password123!

# Todo lo demás se deriva o usa defaults:
# - LDAP_PORT → 389 (default)
# - LDAP_USE_SSL → false (default)
# - LDAP_BASE_DN → DC=empresa,DC=com (derivado de BIND_DN)
# - LDAP_AUTH_TYPE → SIMPLE (default)
# - LDAP_SEARCH_FILTER → (sAMAccountName={username}) (default)
```

### Configuración Completa (Producción)

```env
# Servidor
LDAP_SERVER=dc.empresa.com
LDAP_PORT=636
LDAP_USE_SSL=true

# Autenticación
LDAP_BIND_DN=svc_app@empresa.com
LDAP_BIND_PASSWORD=${VAULT_LDAP_PASSWORD}  # Desde gestor de secretos
LDAP_AUTH_TYPE=SIMPLE

# Base DN (especificado para buscar solo en OU de empleados)
LDAP_BASE_DN=OU=Empleados,DC=empresa,DC=com

# Búsquedas
LDAP_SEARCH_FILTER=(sAMAccountName={username})
```

### Active Directory con SSL

```env
LDAP_SERVER=dc.empresa.local
LDAP_PORT=636
LDAP_USE_SSL=true
LDAP_BIND_DN=ldap_service@empresa.local
LDAP_BIND_PASSWORD=SecurePass2024!
# BASE_DN se deriva automáticamente: DC=empresa,DC=local
```

### OpenLDAP

```env
LDAP_SERVER=ldap.empresa.com
LDAP_PORT=389
LDAP_USE_SSL=false
LDAP_BIND_DN=cn=admin,dc=empresa,dc=com
LDAP_BIND_PASSWORD=admin_password
LDAP_SEARCH_FILTER=(uid={username})
# BASE_DN se deriva automáticamente: dc=empresa,dc=com
```

### Múltiples Ambientes

#### Desarrollo
```env
LDAP_SERVER=ldap-dev.empresa.local
LDAP_BIND_DN=dev_admin@empresa.local
LDAP_BIND_PASSWORD=DevPass123
```

#### Staging
```env
LDAP_SERVER=ldap-stg.empresa.local
LDAP_BIND_DN=stg_admin@empresa.local
LDAP_BIND_PASSWORD=StgPass123
```

#### Producción
```env
LDAP_SERVER=ldap.empresa.com
LDAP_PORT=636
LDAP_USE_SSL=true
LDAP_BIND_DN=prd_svc@empresa.com
LDAP_BIND_PASSWORD=${SECRET_LDAP_PASS}
```

---

## Mejores Prácticas

### 1. Seguridad

```env
# ✅ BIEN: Usar SSL en producción
LDAP_USE_SSL=true
LDAP_PORT=636

# ❌ MAL: Sin cifrado en producción
LDAP_USE_SSL=false
LDAP_PORT=389
```

### 2. Credenciales

```env
# ✅ BIEN: Usuario de servicio dedicado
LDAP_BIND_DN=svc_app_readonly@empresa.com

# ❌ MAL: Usar cuenta de administrador personal
LDAP_BIND_DN=juan.perez@empresa.com
```

### 3. BASE_DN

```env
# ✅ BIEN: Dejar que se derive automáticamente
LDAP_BIND_DN=admin@empresa.com
# (BASE_DN será DC=empresa,DC=com)

# ✅ TAMBIÉN BIEN: Especificar para buscar solo en subárbol
LDAP_BASE_DN=OU=Empleados,DC=empresa,DC=com

# ❌ INNECESARIO: Especificar cuando es redundante
LDAP_BIND_DN=admin@empresa.com
LDAP_BASE_DN=DC=empresa,DC=com  # Redundante, se deriva igual
```

### 4. Formato de BIND_DN

```env
# ✅ MEJOR: Formato UPN (más legible)
LDAP_BIND_DN=admin@empresa.com

# ✅ VÁLIDO: Formato DN completo
LDAP_BIND_DN=CN=admin,DC=empresa,DC=com

# Ambos funcionan igual, pero UPN es más simple
```

### 5. Variables de Entorno vs Parámetros

```python
# ✅ BIEN: Usar variables de entorno
from paquetes.ldap import authenticate_user
if authenticate_user('jperez', 'pass123'):
    print("Autenticado")

# ✅ TAMBIÉN BIEN: Parámetros cuando necesitas múltiples conexiones
from paquetes.ldap import authenticate_user
if authenticate_user('jperez', 'pass123',
                     server='ldap2.empresa.com',
                     base_dn='OU=External,DC=empresa,DC=com'):
    print("Autenticado en servidor secundario")
```

### 6. Gestión de Secretos

```bash
# ✅ BIEN: Usar gestor de secretos
export LDAP_BIND_PASSWORD=$(vault read -field=password secret/ldap)

# ✅ BIEN: Variables de entorno del sistema
export LDAP_BIND_PASSWORD="${LDAP_PASSWORD}"

# ❌ MAL: Hardcodear en archivos
LDAP_BIND_PASSWORD=MiPasswordEnTextoPlano123
```

### 7. Validación

```python
# ✅ BIEN: Validar configuración al inicio
from paquetes.ldap import test_ldap_connection

result = test_ldap_connection()
if not result['success']:
    print(f"ERROR de configuración LDAP: {result['error']}")
    exit(1)

print("✓ Configuración LDAP válida")
```

---

## Referencia Rápida

| Variable | Requerido | Default | Derivable |
|----------|-----------|---------|-----------|
| `LDAP_SERVER` | ✅ Sí | - | ❌ |
| `LDAP_BIND_DN` | ✅ Sí | - | ❌ |
| `LDAP_BIND_PASSWORD` | ✅ Sí | - | ❌ |
| `LDAP_BASE_DN` | ❌ No | Derivado | ✅ Sí |
| `LDAP_PORT` | ❌ No | 389/636 | ❌ |
| `LDAP_USE_SSL` | ❌ No | `false` | ❌ |
| `LDAP_AUTH_TYPE` | ❌ No | `SIMPLE` | ❌ |
| `LDAP_USER_DN_TEMPLATE` | ❌ No | - | ❌ |
| `LDAP_SEARCH_FILTER` | ❌ No | `(sAMAccountName={username})` | ❌ |

---

**Última actualización**: 2026-01-25
**Versión del módulo**: 1.0.0
