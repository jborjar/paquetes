# Módulo Redis - Documentación Completa

Biblioteca completa para operaciones con Redis, el almacén de estructuras de datos en memoria más popular.

> ⚠️ **MÓDULO GENÉRICO**: Este módulo NO tiene valores por defecto hardcodeados. El usuario debe proporcionar TODAS las variables de conexión en el archivo `.env`. Ver [CONFIG.md](../README.md#-configuración) para más detalles.

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Instalación y Configuración](#instalación-y-configuración)
- [Estructura del Módulo](#estructura-del-módulo)
- [Operaciones Básicas](#operaciones-básicas)
- [Operaciones de Caché](#operaciones-de-caché)
- [Estructuras de Datos](#estructuras-de-datos)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Referencia Rápida](#referencia-rápida)
- [Mejores Prácticas](#mejores-prácticas)

---

## Descripción General

El módulo Redis proporciona una interfaz Python simplificada para interactuar con Redis, organizando las operaciones en categorías funcionales:

- **Operaciones Básicas**: GET, SET, DELETE, EXPIRE
- **Operaciones de Caché**: Funciones especializadas para caché con TTL
- **Hashes**: Almacenamiento de objetos estructurados
- **Listas**: Colas, pilas, logs
- **Conjuntos (Sets)**: Colecciones únicas sin orden
- **Contadores**: Incrementos y decrementos atómicos
- **Utilidades**: Información, limpieza, monitoreo

### Características principales

- Interfaz simplificada basada en redis-py
- Serialización automática de JSON
- Manejo automático de conexiones
- Operaciones de caché con expiración
- Soporte para todas las estructuras de datos de Redis
- Funciones atómicas para contadores

---

## Instalación y Configuración

### Requisitos

```bash
pip install redis
```

### Configuración de variables de entorno

⚠️ **El módulo es completamente genérico y NO tiene valores por defecto**.

El usuario DEBE configurar las siguientes variables en el archivo `.env`:

```env
# Redis (REQUERIDO - Sin valores por defecto)
REDIS_HOST=tu_servidor
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=tu_password  # Opcional si no tiene contraseña
```

**Nota**: Si alguna variable no está configurada, el módulo fallará al intentar conectarse. Ver [CONFIG.md](../README.md#-configuración) para documentación completa de configuración.

### Importación del módulo

```python
# Importar todas las funciones
from redis import *

# O importar funciones específicas
from redis import set_value, get_value, cache_set, cache_get
```

---

## Estructura del Módulo

```
redis/
├── __init__.py              # Exporta todas las funciones públicas
└── redis_connection.py      # Todas las operaciones de Redis
```

**Total de funciones**: 35 funciones

---

## Operaciones Básicas

### Conexión a Redis

#### `get_redis_connection(host=None, port=None, db=None, password=None, decode_responses=True)`

Obtiene una conexión activa a Redis.

**Parámetros:**
- `host` (str, opcional): Host del servidor
- `port` (int, opcional): Puerto del servidor
- `db` (int, opcional): Número de base de datos (0-15)
- `password` (str, opcional): Contraseña
- `decode_responses` (bool): Si True, decodifica respuestas a strings

**Retorna:** Cliente redis activo

**Ejemplo:**
```python
redis_client = get_redis_connection()
redis_client = get_redis_connection(db=1)  # Usar BD 1
```

---

### Strings (Operaciones básicas)

#### `set_value(key, value, ex=None, px=None, nx=False, xx=False)`

Establece el valor de una clave.

**Parámetros:**
- `key` (str): Nombre de la clave
- `value` (Any): Valor a almacenar (se serializa automáticamente si es dict/list)
- `ex` (int, opcional): Tiempo de expiración en segundos
- `px` (int, opcional): Tiempo de expiración en milisegundos
- `nx` (bool): Si True, solo establece si la clave NO existe
- `xx` (bool): Si True, solo establece si la clave SI existe

**Retorna:** True si se estableció

**Ejemplo:**
```python
# Simple
set_value('usuario:1:nombre', 'Juan Pérez')

# Con expiración (1 hora)
set_value('sesion:abc123', {'user_id': 1}, ex=3600)

# Solo si no existe
set_value('contador', 0, nx=True)
```

#### `get_value(key, default=None, as_json=False)`

Obtiene el valor de una clave.

**Retorna:** Valor almacenado o default si no existe

**Ejemplo:**
```python
nombre = get_value('usuario:1:nombre')
sesion = get_value('sesion:abc123', as_json=True)
config = get_value('config:timeout', default=30)
```

#### `delete_keys(*keys)`

Elimina una o más claves.

**Retorna:** Número de claves eliminadas

**Ejemplo:**
```python
delete_keys('usuario:1:nombre')
delete_keys('sesion:1', 'sesion:2', 'sesion:3')
```

#### `exists(*keys)`

Verifica si una o más claves existen.

**Retorna:** Número de claves que existen

**Ejemplo:**
```python
if exists('usuario:1:nombre'):
    print('La clave existe')
```

#### `expire(key, seconds)`

Establece tiempo de expiración para una clave.

**Retorna:** True si se estableció

**Ejemplo:**
```python
expire('sesion:abc123', 3600)  # Expira en 1 hora
```

#### `ttl(key)`

Obtiene el tiempo de vida restante de una clave.

**Retorna:** Segundos restantes, -1 si no tiene expiración, -2 si no existe

**Ejemplo:**
```python
tiempo_restante = ttl('sesion:abc123')
if tiempo_restante > 0:
    print(f'Expira en {tiempo_restante} segundos')
```

#### `keys(pattern='*')`

Obtiene claves que coinciden con un patrón.

**Retorna:** Lista de claves que coinciden

**Ejemplo:**
```python
todas_sesiones = keys('sesion:*')
todos_usuarios = keys('usuario:*:nombre')
```

---

## Operaciones de Caché

Funciones especializadas para uso de Redis como caché.

#### `cache_set(key, value, ttl=3600)`

Establece un valor en caché con tiempo de expiración.

**Parámetros:**
- `key` (str): Clave del caché
- `value` (Any): Valor a almacenar
- `ttl` (int): Tiempo de vida en segundos (default: 3600 = 1 hora)

**Ejemplo:**
```python
cache_set('productos:destacados', productos_list, ttl=300)  # 5 minutos
cache_set('usuario:1:perfil', perfil_dict, ttl=1800)  # 30 minutos
```

#### `cache_get(key, default=None, as_json=False)`

Obtiene un valor del caché.

**Ejemplo:**
```python
productos = cache_get('productos:destacados', as_json=True)
if productos is None:
    productos = obtener_productos_db()
    cache_set('productos:destacados', productos)
```

#### `cache_delete(*keys)`

Elimina claves del caché.

**Ejemplo:**
```python
cache_delete('productos:destacados', 'categorias:activas')
```

#### `cache_clear(pattern='*')`

Limpia el caché basado en un patrón.

**Retorna:** Número de claves eliminadas

**Ejemplo:**
```python
cache_clear('usuario:*')  # Limpia todo el caché de usuarios
cache_clear('producto:*')  # Limpia todo el caché de productos
```

---

## Estructuras de Datos

### Hashes

Ideales para almacenar objetos estructurados.

#### `hset(name, key, value)`

Establece el valor de un campo en un hash.

**Ejemplo:**
```python
hset('usuario:1', 'nombre', 'Juan Pérez')
hset('usuario:1', 'email', 'juan@email.com')
hset('usuario:1', 'edad', 30)
```

#### `hget(name, key, as_json=False)`

Obtiene el valor de un campo de un hash.

**Ejemplo:**
```python
nombre = hget('usuario:1', 'nombre')
perfil = hget('usuario:1', 'perfil', as_json=True)
```

#### `hgetall(name)`

Obtiene todos los campos y valores de un hash.

**Retorna:** Diccionario con todos los campos

**Ejemplo:**
```python
usuario = hgetall('usuario:1')
print(f"{usuario['nombre']} - {usuario['email']}")
```

#### `hdel(name, *keys)`

Elimina campos de un hash.

**Ejemplo:**
```python
hdel('usuario:1', 'temporal', 'cache')
```

---

### Listas

Útiles para colas, pilas, logs, historial.

#### `lpush(key, *values)`

Añade valores al inicio de una lista.

**Retorna:** Longitud de la lista después de la operación

**Ejemplo:**
```python
lpush('notificaciones:1', 'Nueva notificación')
lpush('logs:app', log1, log2, log3)
```

#### `rpush(key, *values)`

Añade valores al final de una lista.

**Ejemplo:**
```python
rpush('cola:tareas', 'Tarea 1', 'Tarea 2')
```

#### `lpop(key, as_json=False)`

Obtiene y elimina el primer elemento de una lista.

**Ejemplo:**
```python
notificacion = lpop('notificaciones:1')
```

#### `rpop(key, as_json=False)`

Obtiene y elimina el último elemento de una lista.

**Ejemplo:**
```python
tarea = rpop('cola:tareas')
```

#### `lrange(key, start=0, end=-1)`

Obtiene un rango de elementos de una lista.

**Retorna:** Lista de valores

**Ejemplo:**
```python
todas = lrange('notificaciones:1')
primeras_10 = lrange('notificaciones:1', 0, 9)
ultimas_5 = lrange('notificaciones:1', -5, -1)
```

#### `llen(key)`

Obtiene la longitud de una lista.

**Ejemplo:**
```python
num_notificaciones = llen('notificaciones:1')
```

---

### Conjuntos (Sets)

Para colecciones únicas sin orden.

#### `sadd(key, *members)`

Añade miembros a un conjunto.

**Retorna:** Número de miembros añadidos

**Ejemplo:**
```python
sadd('usuarios:online', 'user:1', 'user:2', 'user:3')
sadd('tags:articulo:123', 'python', 'redis', 'tutorial')
```

#### `srem(key, *members)`

Elimina miembros de un conjunto.

**Ejemplo:**
```python
srem('usuarios:online', 'user:1')
```

#### `smembers(key)`

Obtiene todos los miembros de un conjunto.

**Retorna:** Set con todos los miembros

**Ejemplo:**
```python
usuarios_online = smembers('usuarios:online')
tags = smembers('tags:articulo:123')
```

#### `sismember(key, member)`

Verifica si un miembro pertenece a un conjunto.

**Retorna:** True si pertenece

**Ejemplo:**
```python
if sismember('usuarios:online', 'user:1'):
    print('Usuario está online')
```

#### `scard(key)`

Obtiene el número de miembros en un conjunto.

**Ejemplo:**
```python
num_usuarios_online = scard('usuarios:online')
```

---

### Contadores

Operaciones atómicas para contadores.

#### `incr(key, amount=1)`

Incrementa el valor de una clave.

**Retorna:** Valor después del incremento

**Ejemplo:**
```python
visitas = incr('pagina:visitas')
contador = incr('contador:api', amount=10)
```

#### `decr(key, amount=1)`

Decrementa el valor de una clave.

**Retorna:** Valor después del decremento

**Ejemplo:**
```python
stock = decr('producto:123:stock')
intentos = decr('login:intentos')
```

---

## Ejemplos de Uso

### Ejemplo 1: Sistema de Caché

```python
from redis import cache_set, cache_get, cache_delete

def obtener_productos_destacados():
    """Obtiene productos con caché de 5 minutos."""
    # Intentar obtener del caché
    productos = cache_get('productos:destacados', as_json=True)

    # Si no existe en caché, obtener de BD
    if productos is None:
        productos = obtener_productos_desde_bd()
        cache_set('productos:destacados', productos, ttl=300)

    return productos

def actualizar_producto(producto_id):
    """Actualiza producto e invalida caché."""
    # Actualizar en BD
    actualizar_en_bd(producto_id)

    # Invalidar caché
    cache_delete('productos:destacados')
```

### Ejemplo 2: Sistema de Sesiones

```python
from redis import set_value, get_value, delete_keys, ttl
import uuid

def crear_sesion(user_id):
    """Crea una sesión de usuario."""
    session_id = str(uuid.uuid4())
    session_data = {
        'user_id': user_id,
        'created_at': datetime.now().isoformat()
    }

    # Sesión expira en 1 hora
    set_value(f'sesion:{session_id}', session_data, ex=3600)
    return session_id

def obtener_sesion(session_id):
    """Obtiene datos de sesión."""
    return get_value(f'sesion:{session_id}', as_json=True)

def renovar_sesion(session_id):
    """Renueva tiempo de expiración de sesión."""
    if exists(f'sesion:{session_id}'):
        expire(f'sesion:{session_id}', 3600)  # 1 hora más
        return True
    return False

def cerrar_sesion(session_id):
    """Elimina sesión."""
    delete_keys(f'sesion:{session_id}')
```

### Ejemplo 3: Cola de Tareas

```python
from redis import rpush, lpop, lrange, llen

def agregar_tarea(tarea):
    """Añade tarea a la cola."""
    rpush('cola:tareas', tarea)

def obtener_tarea():
    """Obtiene y procesa la siguiente tarea."""
    tarea = lpop('cola:tareas', as_json=True)
    if tarea:
        procesar_tarea(tarea)
    return tarea

def ver_tareas_pendientes():
    """Ver todas las tareas sin procesarlas."""
    return lrange('cola:tareas')

def contador_tareas():
    """Obtener número de tareas pendientes."""
    return llen('cola:tareas')
```

### Ejemplo 4: Usuarios Online

```python
from redis import sadd, srem, smembers, scard

def marcar_usuario_online(user_id):
    """Marca usuario como online."""
    sadd('usuarios:online', f'user:{user_id}')

def marcar_usuario_offline(user_id):
    """Marca usuario como offline."""
    srem('usuarios:online', f'user:{user_id}')

def obtener_usuarios_online():
    """Obtiene lista de usuarios online."""
    return smembers('usuarios:online')

def contador_usuarios_online():
    """Obtiene número de usuarios online."""
    return scard('usuarios:online')
```

### Ejemplo 5: Contadores y Estadísticas

```python
from redis import incr, decr, get_value

def registrar_visita(pagina):
    """Registra visita a una página."""
    incr(f'visitas:{pagina}')
    incr('visitas:total')

def obtener_visitas(pagina):
    """Obtiene número de visitas."""
    return int(get_value(f'visitas:{pagina}', default=0))

def registrar_compra(producto_id):
    """Registra compra y actualiza stock."""
    incr(f'ventas:producto:{producto_id}')
    stock = decr(f'stock:producto:{producto_id}')

    if stock <= 0:
        # Alertar stock bajo
        set_value(f'alerta:stock:{producto_id}', True)

    return stock
```

---

## Referencia Rápida

### Operaciones Básicas (7 funciones)

| Función | Descripción |
|---------|-------------|
| `set_value()` | Establece valor de una clave |
| `get_value()` | Obtiene valor de una clave |
| `delete_keys()` | Elimina claves |
| `exists()` | Verifica si existe una clave |
| `expire()` | Establece tiempo de expiración |
| `ttl()` | Obtiene tiempo de vida restante |
| `keys()` | Obtiene claves por patrón |

### Operaciones de Caché (4 funciones)

| Función | Descripción |
|---------|-------------|
| `cache_set()` | Guarda en caché con TTL |
| `cache_get()` | Obtiene del caché |
| `cache_delete()` | Elimina del caché |
| `cache_clear()` | Limpia caché por patrón |

### Hashes (4 funciones)

| Función | Descripción |
|---------|-------------|
| `hset()` | Establece campo en hash |
| `hget()` | Obtiene campo de hash |
| `hgetall()` | Obtiene todos los campos |
| `hdel()` | Elimina campos de hash |

### Listas (6 funciones)

| Función | Descripción |
|---------|-------------|
| `lpush()` | Añade al inicio |
| `rpush()` | Añade al final |
| `lpop()` | Obtiene y elimina del inicio |
| `rpop()` | Obtiene y elimina del final |
| `lrange()` | Obtiene rango de elementos |
| `llen()` | Obtiene longitud |

### Conjuntos (5 funciones)

| Función | Descripción |
|---------|-------------|
| `sadd()` | Añade miembros |
| `srem()` | Elimina miembros |
| `smembers()` | Obtiene todos los miembros |
| `sismember()` | Verifica pertenencia |
| `scard()` | Cuenta miembros |

### Contadores (2 funciones)

| Función | Descripción |
|---------|-------------|
| `incr()` | Incrementa valor |
| `decr()` | Decrementa valor |

### Utilidades (4 funciones)

| Función | Descripción |
|---------|-------------|
| `ping()` | Verifica conexión |
| `flushdb()` | Limpia base de datos |
| `dbsize()` | Número de claves |
| `info()` | Información del servidor |

---

## Mejores Prácticas

### 1. Usar nombres de claves descriptivos y consistentes

**✅ CORRECTO:**
```python
set_value('usuario:123:nombre', 'Juan')
set_value('sesion:abc123:data', session_data)
set_value('cache:productos:destacados', productos)
```

**❌ INCORRECTO:**
```python
set_value('u123n', 'Juan')
set_value('session', session_data)
set_value('prods', productos)
```

### 2. Siempre establecer TTL para caché temporal

```python
# Caché de 5 minutos
cache_set('productos:destacados', productos, ttl=300)

# Sesiones de 1 hora
set_value('sesion:abc123', datos, ex=3600)
```

### 3. Usar estructuras de datos apropiadas

- **Strings**: Valores simples, contadores
- **Hashes**: Objetos estructurados (usuario, configuración)
- **Listas**: Colas, logs, historial
- **Sets**: Tags, usuarios online, colecciones únicas

### 4. Limpiar claves obsoletas

```python
# Limpiar sesiones expiradas (no necesario con TTL)
# Limpiar caché de un módulo
cache_clear('modulo:*')
```

### 5. Usar operaciones atómicas para contadores

**✅ CORRECTO:**
```python
incr('visitas:pagina:home')  # Atómico, thread-safe
```

**❌ INCORRECTO:**
```python
visitas = int(get_value('visitas:pagina:home', default=0))
visitas += 1
set_value('visitas:pagina:home', visitas)  # Race condition!
```

### 6. Verificar conexión antes de operaciones críticas

```python
if ping():
    # Redis está disponible
    cache_set('data', datos)
else:
    # Usar fallback (BD, archivo, etc.)
    guardar_en_bd(datos)
```

---

**Versión:** 1.0.0
**Compatible con:** Redis 5.0+
**Dependencias:** redis >= 4.0
