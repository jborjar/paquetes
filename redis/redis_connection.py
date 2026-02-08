"""
Módulo Redis - Operaciones completas para Redis.

Este módulo proporciona funciones para interactuar con Redis:
- Operaciones básicas (GET, SET, DELETE)
- Operaciones de caché con expiración
- Estructuras de datos (Strings, Lists, Sets, Hashes, Sorted Sets)
- Pub/Sub
- Utilidades

⚠️ MÓDULO GENÉRICO: No depende de ningún archivo de configuración específico.
Las credenciales se pasan como parámetros o se leen de variables de entorno.
"""
import redis
import os
import json
from typing import Any, Dict, List, Optional, Union


def get_redis_connection(
    host: str | None = None,
    port: int | None = None,
    db: int | None = None,
    password: str | None = None,
    decode_responses: bool = True
) -> redis.Redis:
    """
    Obtiene conexión a Redis.

    Args:
        host: Host del servidor Redis (opcional, lee de REDIS_HOST si es None)
        port: Puerto del servidor (opcional, lee de REDIS_PORT si es None)
        db: Número de base de datos (opcional, lee de REDIS_DB si es None)
        password: Contraseña (opcional, lee de REDIS_PASSWORD si es None)
        decode_responses: Si True, decodifica respuestas a strings (default: True)

    Returns:
        Cliente redis activo

    Example:
        # Usando variables de entorno
        redis_client = get_redis_connection()

        # Pasando credenciales directamente
        redis_client = get_redis_connection(
            host='localhost',
            port=6379,
            db=0,
            password='mi_password'
        )
    """
    # Leer de parámetros o variables de entorno
    host = host or os.getenv('REDIS_HOST', 'localhost')
    port = port or int(os.getenv('REDIS_PORT', '6379'))
    db = db if db is not None else int(os.getenv('REDIS_DB', '0'))
    password = password or os.getenv('REDIS_PASSWORD', None)

    return redis.Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=decode_responses
    )


# ============================================================================
# OPERACIONES BÁSICAS (STRINGS)
# ============================================================================

def set_value(
    key: str,
    value: Any,
    ex: int | None = None,
    px: int | None = None,
    nx: bool = False,
    xx: bool = False
) -> bool:
    """
    Establece el valor de una clave.

    Args:
        key: Nombre de la clave
        value: Valor a almacenar (se serializa automáticamente si es dict/list)
        ex: Tiempo de expiración en segundos (opcional)
        px: Tiempo de expiración en milisegundos (opcional)
        nx: Si True, solo establece si la clave NO existe (SET IF NOT EXISTS)
        xx: Si True, solo establece si la clave SI existe (SET IF EXISTS)

    Returns:
        True si se estableció, False si no (cuando se usa nx o xx)

    Example:
        set_value('usuario:1:nombre', 'Juan Pérez')
        set_value('sesion:abc123', {'user_id': 1}, ex=3600)  # Expira en 1 hora
        set_value('contador', 0, nx=True)  # Solo si no existe
    """
    redis_client = get_redis_connection()

    # Serializar valor si es necesario
    if isinstance(value, (dict, list)):
        value = json.dumps(value)

    return redis_client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)


def get_value(
    key: str,
    default: Any = None,
    as_json: bool = False
) -> Any:
    """
    Obtiene el valor de una clave.

    Args:
        key: Nombre de la clave
        default: Valor por defecto si la clave no existe
        as_json: Si True, deserializa el valor como JSON

    Returns:
        Valor almacenado o default si no existe

    Example:
        nombre = get_value('usuario:1:nombre')
        sesion = get_value('sesion:abc123', as_json=True)
        config = get_value('config:timeout', default=30)
    """
    redis_client = get_redis_connection()
    value = redis_client.get(key)

    if value is None:
        return default

    if as_json:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return value


def delete_keys(*keys: str) -> int:
    """
    Elimina una o más claves.

    Args:
        *keys: Claves a eliminar

    Returns:
        Número de claves eliminadas

    Example:
        delete_keys('usuario:1:nombre')
        delete_keys('sesion:1', 'sesion:2', 'sesion:3')
    """
    redis_client = get_redis_connection()
    return redis_client.delete(*keys)


def exists(*keys: str) -> int:
    """
    Verifica si una o más claves existen.

    Args:
        *keys: Claves a verificar

    Returns:
        Número de claves que existen

    Example:
        if exists('usuario:1:nombre'):
            print('La clave existe')

        count = exists('key1', 'key2', 'key3')
        print(f'{count} claves existen')
    """
    redis_client = get_redis_connection()
    return redis_client.exists(*keys)


def expire(key: str, seconds: int) -> bool:
    """
    Establece tiempo de expiración para una clave.

    Args:
        key: Nombre de la clave
        seconds: Segundos hasta expirar

    Returns:
        True si se estableció, False si la clave no existe

    Example:
        expire('sesion:abc123', 3600)  # Expira en 1 hora
    """
    redis_client = get_redis_connection()
    return redis_client.expire(key, seconds)


def ttl(key: str) -> int:
    """
    Obtiene el tiempo de vida restante de una clave.

    Args:
        key: Nombre de la clave

    Returns:
        Segundos restantes, -1 si no tiene expiración, -2 si no existe

    Example:
        tiempo_restante = ttl('sesion:abc123')
        if tiempo_restante > 0:
            print(f'Expira en {tiempo_restante} segundos')
    """
    redis_client = get_redis_connection()
    return redis_client.ttl(key)


def keys(pattern: str = '*') -> List[str]:
    """
    Obtiene claves que coinciden con un patrón.

    Args:
        pattern: Patrón de búsqueda (* = todos)

    Returns:
        Lista de claves que coinciden

    Example:
        todas_sesiones = keys('sesion:*')
        todos_usuarios = keys('usuario:*:nombre')
    """
    redis_client = get_redis_connection()
    return [key.decode() if isinstance(key, bytes) else key for key in redis_client.keys(pattern)]


# ============================================================================
# OPERACIONES DE CACHÉ
# ============================================================================

def cache_set(
    key: str,
    value: Any,
    ttl: int = 3600
) -> bool:
    """
    Establece un valor en caché con tiempo de expiración.

    Args:
        key: Clave del caché
        value: Valor a almacenar
        ttl: Tiempo de vida en segundos (default: 3600 = 1 hora)

    Returns:
        True si se estableció exitosamente

    Example:
        cache_set('productos:destacados', productos_list, ttl=300)  # 5 minutos
    """
    return set_value(key, value, ex=ttl)


def cache_get(
    key: str,
    default: Any = None,
    as_json: bool = False
) -> Any:
    """
    Obtiene un valor del caché.

    Args:
        key: Clave del caché
        default: Valor por defecto si no existe o expiró
        as_json: Si True, deserializa como JSON

    Returns:
        Valor almacenado o default

    Example:
        productos = cache_get('productos:destacados', as_json=True)
        if productos is None:
            productos = obtener_productos_db()
            cache_set('productos:destacados', productos)
    """
    return get_value(key, default=default, as_json=as_json)


def cache_delete(*keys: str) -> int:
    """
    Elimina claves del caché.

    Args:
        *keys: Claves a eliminar

    Returns:
        Número de claves eliminadas

    Example:
        cache_delete('productos:destacados', 'categorias:activas')
    """
    return delete_keys(*keys)


def cache_clear(pattern: str = '*') -> int:
    """
    Limpia el caché basado en un patrón.

    Args:
        pattern: Patrón de claves a eliminar

    Returns:
        Número de claves eliminadas

    Example:
        cache_clear('usuario:*')  # Limpia todo el caché de usuarios
        cache_clear('sesion:*')   # Limpia todas las sesiones
    """
    redis_client = get_redis_connection()
    claves = redis_client.keys(pattern)
    if claves:
        return redis_client.delete(*claves)
    return 0


# ============================================================================
# OPERACIONES DE HASH
# ============================================================================

def hset(name: str, key: str, value: Any) -> int:
    """
    Establece el valor de un campo en un hash.

    Args:
        name: Nombre del hash
        key: Campo del hash
        value: Valor a almacenar

    Returns:
        1 si se creó un nuevo campo, 0 si se actualizó

    Example:
        hset('usuario:1', 'nombre', 'Juan Pérez')
        hset('usuario:1', 'email', 'juan@email.com')
    """
    redis_client = get_redis_connection()
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    return redis_client.hset(name, key, value)


def hget(name: str, key: str, as_json: bool = False) -> Any:
    """
    Obtiene el valor de un campo de un hash.

    Args:
        name: Nombre del hash
        key: Campo del hash
        as_json: Si True, deserializa como JSON

    Returns:
        Valor del campo o None si no existe

    Example:
        nombre = hget('usuario:1', 'nombre')
        perfil = hget('usuario:1', 'perfil', as_json=True)
    """
    redis_client = get_redis_connection()
    value = redis_client.hget(name, key)

    if value is None:
        return None

    if as_json:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return value


def hgetall(name: str) -> Dict[str, Any]:
    """
    Obtiene todos los campos y valores de un hash.

    Args:
        name: Nombre del hash

    Returns:
        Diccionario con todos los campos y valores

    Example:
        usuario = hgetall('usuario:1')
        print(usuario['nombre'])
    """
    redis_client = get_redis_connection()
    return redis_client.hgetall(name)


def hdel(name: str, *keys: str) -> int:
    """
    Elimina campos de un hash.

    Args:
        name: Nombre del hash
        *keys: Campos a eliminar

    Returns:
        Número de campos eliminados

    Example:
        hdel('usuario:1', 'temporal', 'cache')
    """
    redis_client = get_redis_connection()
    return redis_client.hdel(name, *keys)


# ============================================================================
# OPERACIONES DE LISTA
# ============================================================================

def lpush(key: str, *values: Any) -> int:
    """
    Añade valores al inicio de una lista.

    Args:
        key: Nombre de la lista
        *values: Valores a añadir

    Returns:
        Longitud de la lista después de la operación

    Example:
        lpush('notificaciones:1', 'Nueva notificación')
        lpush('logs:app', log1, log2, log3)
    """
    redis_client = get_redis_connection()
    serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
    return redis_client.lpush(key, *serialized)


def rpush(key: str, *values: Any) -> int:
    """
    Añade valores al final de una lista.

    Args:
        key: Nombre de la lista
        *values: Valores a añadir

    Returns:
        Longitud de la lista después de la operación

    Example:
        rpush('cola:tareas', 'Tarea 1', 'Tarea 2')
    """
    redis_client = get_redis_connection()
    serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
    return redis_client.rpush(key, *serialized)


def lpop(key: str, as_json: bool = False) -> Any:
    """
    Obtiene y elimina el primer elemento de una lista.

    Args:
        key: Nombre de la lista
        as_json: Si True, deserializa como JSON

    Returns:
        Valor del primer elemento o None

    Example:
        notificacion = lpop('notificaciones:1')
    """
    redis_client = get_redis_connection()
    value = redis_client.lpop(key)

    if value is None:
        return None

    if as_json:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return value


def rpop(key: str, as_json: bool = False) -> Any:
    """
    Obtiene y elimina el último elemento de una lista.

    Args:
        key: Nombre de la lista
        as_json: Si True, deserializa como JSON

    Returns:
        Valor del último elemento o None

    Example:
        tarea = rpop('cola:tareas')
    """
    redis_client = get_redis_connection()
    value = redis_client.rpop(key)

    if value is None:
        return None

    if as_json:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return value


def lrange(key: str, start: int = 0, end: int = -1) -> List[Any]:
    """
    Obtiene un rango de elementos de una lista.

    Args:
        key: Nombre de la lista
        start: Índice de inicio (default: 0)
        end: Índice de fin (default: -1 = hasta el final)

    Returns:
        Lista de valores

    Example:
        todas = lrange('notificaciones:1')
        primeras_10 = lrange('notificaciones:1', 0, 9)
    """
    redis_client = get_redis_connection()
    return redis_client.lrange(key, start, end)


def llen(key: str) -> int:
    """
    Obtiene la longitud de una lista.

    Args:
        key: Nombre de la lista

    Returns:
        Longitud de la lista

    Example:
        num_notificaciones = llen('notificaciones:1')
    """
    redis_client = get_redis_connection()
    return redis_client.llen(key)


# ============================================================================
# OPERACIONES DE CONJUNTO (SETS)
# ============================================================================

def sadd(key: str, *members: Any) -> int:
    """
    Añade miembros a un conjunto.

    Args:
        key: Nombre del conjunto
        *members: Miembros a añadir

    Returns:
        Número de miembros añadidos (no cuenta duplicados)

    Example:
        sadd('usuarios:online', 'user:1', 'user:2', 'user:3')
    """
    redis_client = get_redis_connection()
    return redis_client.sadd(key, *members)


def srem(key: str, *members: Any) -> int:
    """
    Elimina miembros de un conjunto.

    Args:
        key: Nombre del conjunto
        *members: Miembros a eliminar

    Returns:
        Número de miembros eliminados

    Example:
        srem('usuarios:online', 'user:1')
    """
    redis_client = get_redis_connection()
    return redis_client.srem(key, *members)


def smembers(key: str) -> set:
    """
    Obtiene todos los miembros de un conjunto.

    Args:
        key: Nombre del conjunto

    Returns:
        Set con todos los miembros

    Example:
        usuarios_online = smembers('usuarios:online')
    """
    redis_client = get_redis_connection()
    return redis_client.smembers(key)


def sismember(key: str, member: Any) -> bool:
    """
    Verifica si un miembro pertenece a un conjunto.

    Args:
        key: Nombre del conjunto
        member: Miembro a verificar

    Returns:
        True si pertenece, False si no

    Example:
        if sismember('usuarios:online', 'user:1'):
            print('Usuario está online')
    """
    redis_client = get_redis_connection()
    return redis_client.sismember(key, member)


def scard(key: str) -> int:
    """
    Obtiene el número de miembros en un conjunto.

    Args:
        key: Nombre del conjunto

    Returns:
        Número de miembros

    Example:
        num_usuarios_online = scard('usuarios:online')
    """
    redis_client = get_redis_connection()
    return redis_client.scard(key)


# ============================================================================
# OPERACIONES DE CONTADOR
# ============================================================================

def incr(key: str, amount: int = 1) -> int:
    """
    Incrementa el valor de una clave.

    Args:
        key: Nombre de la clave
        amount: Cantidad a incrementar (default: 1)

    Returns:
        Valor después del incremento

    Example:
        visitas = incr('pagina:visitas')
        contador = incr('contador:api', amount=10)
    """
    redis_client = get_redis_connection()
    return redis_client.incr(key, amount)


def decr(key: str, amount: int = 1) -> int:
    """
    Decrementa el valor de una clave.

    Args:
        key: Nombre de la clave
        amount: Cantidad a decrementar (default: 1)

    Returns:
        Valor después del decremento

    Example:
        stock = decr('producto:123:stock')
        intentos = decr('login:intentos', amount=1)
    """
    redis_client = get_redis_connection()
    return redis_client.decr(key, amount)


# ============================================================================
# UTILIDADES
# ============================================================================

def ping() -> bool:
    """
    Verifica la conexión con Redis.

    Returns:
        True si la conexión es exitosa

    Example:
        if ping():
            print('Redis está conectado')
    """
    try:
        redis_client = get_redis_connection()
        return redis_client.ping()
    except:
        return False


def flushdb() -> bool:
    """
    Elimina todas las claves de la base de datos actual.

    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.

    Returns:
        True si se ejecutó exitosamente

    Example:
        flushdb()  # Limpia toda la BD actual
    """
    redis_client = get_redis_connection()
    return redis_client.flushdb()


def dbsize() -> int:
    """
    Obtiene el número de claves en la base de datos actual.

    Returns:
        Número de claves

    Example:
        total_claves = dbsize()
        print(f'Total de claves: {total_claves}')
    """
    redis_client = get_redis_connection()
    return redis_client.dbsize()


def info(section: str | None = None) -> Dict[str, Any]:
    """
    Obtiene información y estadísticas del servidor Redis.

    Args:
        section: Sección específica (server, clients, memory, stats, etc.)

    Returns:
        Diccionario con información

    Example:
        info_general = info()
        info_memoria = info('memory')
    """
    redis_client = get_redis_connection()
    return redis_client.info(section)
