"""
Módulo Redis - Operaciones completas para Redis.

Este módulo proporciona funciones para interactuar con Redis:
- Operaciones básicas (GET, SET, DELETE)
- Operaciones de caché con expiración
- Estructuras de datos (Strings, Lists, Sets, Hashes)
- Contadores
- Utilidades
"""

from .redis_connection import (
    # Conexión
    get_redis_connection,
    # Operaciones básicas
    set_value,
    get_value,
    delete_keys,
    exists,
    expire,
    ttl,
    keys,
    # Operaciones de caché
    cache_set,
    cache_get,
    cache_delete,
    cache_clear,
    # Operaciones de Hash
    hset,
    hget,
    hgetall,
    hdel,
    # Operaciones de Lista
    lpush,
    rpush,
    lpop,
    rpop,
    lrange,
    llen,
    # Operaciones de Conjunto (Sets)
    sadd,
    srem,
    smembers,
    sismember,
    scard,
    # Contadores
    incr,
    decr,
    # Utilidades
    ping,
    flushdb,
    dbsize,
    info
)

__all__ = [
    # Conexión
    "get_redis_connection",

    # Operaciones básicas (Strings)
    "set_value",
    "get_value",
    "delete_keys",
    "exists",
    "expire",
    "ttl",
    "keys",

    # Operaciones de caché
    "cache_set",
    "cache_get",
    "cache_delete",
    "cache_clear",

    # Operaciones de Hash
    "hset",
    "hget",
    "hgetall",
    "hdel",

    # Operaciones de Lista
    "lpush",
    "rpush",
    "lpop",
    "rpop",
    "lrange",
    "llen",

    # Operaciones de Conjunto (Sets)
    "sadd",
    "srem",
    "smembers",
    "sismember",
    "scard",

    # Contadores
    "incr",
    "decr",

    # Utilidades
    "ping",
    "flushdb",
    "dbsize",
    "info"
]
