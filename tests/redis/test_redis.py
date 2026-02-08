"""
Script de pruebas para el módulo Redis.

Este script prueba las funcionalidades básicas del módulo redis.
"""
from paquetes.redis import (
    ping, set_value, get_value, delete_keys,
    cache_set, cache_get, cache_delete,
    hset, hget, hgetall,
    lpush, rpush, lpop, lrange,
    sadd, smembers, scard,
    incr, decr
)


def test_conexion():
    """Prueba la conexión a Redis."""
    print("\n=== TEST: Conexión a Redis ===")
    try:
        if ping():
            print("✓ Conexión exitosa")
            return True
        else:
            print("✗ No se pudo conectar a Redis")
            return False
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False


def test_operaciones_basicas():
    """Prueba operaciones básicas con strings."""
    print("\n=== TEST: Operaciones Básicas (Strings) ===")

    try:
        # SET y GET
        print("Estableciendo valor...")
        set_value('test:nombre', 'Juan Pérez')
        nombre = get_value('test:nombre')
        assert nombre == 'Juan Pérez', "El valor no coincide"
        print(f"✓ SET/GET: {nombre}")

        # SET con expiración
        print("Estableciendo valor con TTL...")
        set_value('test:temporal', 'Valor temporal', ex=10)
        temporal = get_value('test:temporal')
        assert temporal == 'Valor temporal'
        print("✓ SET con expiración")

        # DELETE
        print("Eliminando clave...")
        delete_keys('test:nombre', 'test:temporal')
        print("✓ DELETE")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_cache():
    """Prueba operaciones de caché."""
    print("\n=== TEST: Operaciones de Caché ===")

    try:
        # Cache SET
        print("Guardando en caché...")
        cache_set('test:cache:productos', {'id': 1, 'nombre': 'Producto 1'}, ttl=60)
        print("✓ Cache SET")

        # Cache GET
        print("Obteniendo del caché...")
        producto = cache_get('test:cache:productos', as_json=True)
        assert producto['nombre'] == 'Producto 1'
        print(f"✓ Cache GET: {producto}")

        # Cache DELETE
        print("Eliminando del caché...")
        cache_delete('test:cache:productos')
        print("✓ Cache DELETE")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_hash():
    """Prueba operaciones con hashes."""
    print("\n=== TEST: Operaciones de Hash ===")

    try:
        # HSET
        print("Estableciendo campos en hash...")
        hset('test:usuario:1', 'nombre', 'Juan')
        hset('test:usuario:1', 'email', 'juan@email.com')
        hset('test:usuario:1', 'edad', '30')
        print("✓ HSET")

        # HGET
        print("Obteniendo campo...")
        nombre = hget('test:usuario:1', 'nombre')
        assert nombre == 'Juan'
        print(f"✓ HGET: {nombre}")

        # HGETALL
        print("Obteniendo todos los campos...")
        usuario = hgetall('test:usuario:1')
        print(f"✓ HGETALL: {usuario}")

        # Limpiar
        delete_keys('test:usuario:1')

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_listas():
    """Prueba operaciones con listas."""
    print("\n=== TEST: Operaciones de Lista ===")

    try:
        # LPUSH y RPUSH
        print("Añadiendo elementos a la lista...")
        lpush('test:lista', 'primero')
        rpush('test:lista', 'segundo', 'tercero')
        print("✓ PUSH")

        # LRANGE
        print("Obteniendo elementos...")
        elementos = lrange('test:lista')
        print(f"✓ LRANGE: {elementos}")

        # LPOP
        print("Extrayendo primer elemento...")
        primero = lpop('test:lista')
        print(f"✓ LPOP: {primero}")

        # Limpiar
        delete_keys('test:lista')

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_sets():
    """Prueba operaciones con conjuntos."""
    print("\n=== TEST: Operaciones de Conjunto (Set) ===")

    try:
        # SADD
        print("Añadiendo miembros al conjunto...")
        sadd('test:usuarios:online', 'user:1', 'user:2', 'user:3')
        print("✓ SADD")

        # SMEMBERS
        print("Obteniendo miembros...")
        usuarios = smembers('test:usuarios:online')
        print(f"✓ SMEMBERS: {usuarios}")

        # SCARD
        print("Contando miembros...")
        count = scard('test:usuarios:online')
        assert count == 3
        print(f"✓ SCARD: {count}")

        # Limpiar
        delete_keys('test:usuarios:online')

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_contadores():
    """Prueba operaciones de contadores."""
    print("\n=== TEST: Contadores ===")

    try:
        # INCR
        print("Incrementando contador...")
        val1 = incr('test:contador')
        val2 = incr('test:contador')
        val3 = incr('test:contador', amount=10)
        print(f"✓ INCR: {val1} -> {val2} -> {val3}")

        # DECR
        print("Decrementando contador...")
        val4 = decr('test:contador', amount=5)
        print(f"✓ DECR: {val4}")

        # Limpiar
        delete_keys('test:contador')

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("=" * 60)
    print("PRUEBAS DEL MÓDULO REDIS")
    print("=" * 60)

    resultados = []

    # Prueba de conexión
    resultados.append(('Conexión', test_conexion()))

    # Si la conexión falla, no continuar
    if not resultados[0][1]:
        print("\n✗ No se pudo conectar a Redis. Verifica la configuración.")
        return

    # Pruebas de funcionalidad
    resultados.append(('Operaciones Básicas', test_operaciones_basicas()))
    resultados.append(('Caché', test_cache()))
    resultados.append(('Hash', test_hash()))
    resultados.append(('Listas', test_listas()))
    resultados.append(('Sets', test_sets()))
    resultados.append(('Contadores', test_contadores()))

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)

    exitosas = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nombre, resultado in resultados:
        estado = "✓ PASÓ" if resultado else "✗ FALLÓ"
        print(f"{estado} - {nombre}")

    print(f"\nTotal: {exitosas}/{total} pruebas exitosas")

    if exitosas == total:
        print("\n✓ TODAS LAS PRUEBAS PASARON")
    else:
        print("\n✗ ALGUNAS PRUEBAS FALLARON")


if __name__ == '__main__':
    main()
