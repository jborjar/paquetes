"""
Gestión de sesiones de usuario con sliding expiration.

Maneja sesiones con soporte para múltiples backends de almacenamiento.
Portable y genérico - funciona con JSON, MSSQL u otros backends.
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from .storage import SessionStorage
from .storage_json import JSONSessionStorage

# Storage backend global (configurable)
_storage: Optional[SessionStorage] = None


def configure_storage(storage: SessionStorage):
    """
    Configura el backend de almacenamiento para las sesiones.

    Args:
        storage: Instancia de SessionStorage (JSONSessionStorage, MSSQLSessionStorage, etc.)

    Example:
        >>> from paquetes.auth import configure_storage
        >>> from paquetes.auth.storage_json import JSONSessionStorage
        >>> configure_storage(JSONSessionStorage('sessions.json'))
    """
    global _storage
    _storage = storage


def _get_storage() -> SessionStorage:
    """
    Obtiene el backend de almacenamiento configurado.
    Si no se ha configurado, usa JSONSessionStorage por defecto.
    """
    global _storage
    if _storage is None:
        # Default: JSON storage
        sessions_file = os.getenv('AUTH_SESSIONS_FILE', 'sessions.json')
        _storage = JSONSessionStorage(sessions_file)
    return _storage


def _get_expiration_minutes() -> int:
    """Obtiene timeout de sesión desde variable de entorno."""
    return int(os.getenv('JWT_EXPIRATION_MINUTES', '30'))


def ensure_sessions_table():
    """
    Crea la estructura necesaria para almacenar sesiones.

    Dependiendo del backend configurado:
    - JSON: Crea el archivo JSON si no existe
    - MSSQL: Crea la tabla USER_SESSIONS
    - Otros: Ejecuta la lógica específica del backend
    """
    storage = _get_storage()
    storage.ensure_table()


def create_session(username: str, scopes: Optional[str] = None) -> Dict[str, str]:
    """
    Crea una nueva sesión para un usuario.

    Controla el límite de sesiones activas por usuario. Si el usuario
    excede el límite configurado en su campo MaxSessions, se elimina
    automáticamente su sesión más antigua.

    Args:
        username: Nombre del usuario
        scopes: Permisos/alcances de la sesión (opcional)

    Returns:
        Dict con session_id, username, created_at, expires_at

    Example:
        >>> session = create_session('admin', 'read:users,write:users')
        >>> print(session['session_id'])
        'a1b2c3d4-...'
    """
    ensure_sessions_table()

    storage = _get_storage()
    expiration_minutes = _get_expiration_minutes()

    # Obtener límite de sesiones del usuario desde la BD
    max_sessions = storage.get_user_max_sessions(username)

    # Verificar sesiones activas del usuario
    active_sessions = storage.count_active_sessions(username, expiration_minutes)

    # Si excede el límite, eliminar sesiones más antiguas hasta cumplir el límite
    while active_sessions >= max_sessions:
        oldest_session = storage.get_oldest_session(username, expiration_minutes)
        if oldest_session:
            storage.delete_session(oldest_session['session_id'])
            active_sessions -= 1
        else:
            break

    # Crear nueva sesión
    session_id = str(uuid.uuid4())
    now = datetime.now()

    storage.create_session(
        session_id=session_id,
        username=username,
        created_at=now,
        last_activity=now,
        scopes=scopes
    )

    return {
        'session_id': session_id,
        'username': username,
        'created_at': now.isoformat(),
        'expires_at': (now + timedelta(minutes=expiration_minutes)).isoformat(),
        'scopes': scopes
    }


def validate_session(session_id: str, renew: bool = True) -> Optional[Dict[str, str]]:
    """
    Valida una sesión y opcionalmente la renueva (sliding expiration).

    Args:
        session_id: ID de la sesión a validar
        renew: Si True, renueva la sesión actualizando LastActivity

    Returns:
        Dict con datos de la sesión si es válida, None si expiró o no existe

    Example:
        >>> session = validate_session('a1b2c3d4-...')
        >>> if session:
        ...     print(f"Usuario: {session['username']}")
        >>> else:
        ...     print("Sesión inválida o expirada")
    """
    storage = _get_storage()
    expiration_minutes = _get_expiration_minutes()

    # Buscar sesión activa
    session = storage.get_session(session_id)

    if not session:
        return None

    # Verificar si expiró
    # Manejar tanto string como datetime object
    last_activity = session['last_activity']
    if isinstance(last_activity, str):
        last_activity = datetime.fromisoformat(last_activity)

    if datetime.now() > last_activity + timedelta(minutes=expiration_minutes):
        return None

    # Renovar sesión si se solicita (sliding expiration)
    if renew:
        now = datetime.now()
        storage.update_last_activity(session_id, now)
        last_activity = now

    # Manejar created_at también
    created_at = session['created_at']
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)

    return {
        'session_id': session['session_id'],
        'username': session['username'],
        'created_at': created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
        'last_activity': last_activity.isoformat(),
        'expires_at': (last_activity + timedelta(minutes=expiration_minutes)).isoformat(),
        'scopes': session.get('scopes')
    }


def delete_session(session_id: str) -> bool:
    """
    Elimina una sesión (logout).

    Args:
        session_id: ID de la sesión a eliminar

    Returns:
        True si se eliminó la sesión, False si no existía

    Example:
        >>> success = delete_session('a1b2c3d4-...')
        >>> if success:
        ...     print("Sesión cerrada")
    """
    storage = _get_storage()
    return storage.delete_session(session_id)


def delete_user_sessions(username: str) -> int:
    """
    Elimina todas las sesiones de un usuario.

    Args:
        username: Nombre del usuario

    Returns:
        Número de sesiones eliminadas

    Example:
        >>> count = delete_user_sessions('admin')
        >>> print(f"Sesiones cerradas: {count}")
    """
    storage = _get_storage()
    return storage.delete_user_sessions(username)


def cleanup_expired_sessions() -> int:
    """
    Elimina sesiones expiradas del almacenamiento.

    Se recomienda ejecutar periódicamente (cron job) para mantener
    el almacenamiento limpio.

    Returns:
        Número de sesiones eliminadas

    Example:
        >>> count = cleanup_expired_sessions()
        >>> print(f"Sesiones expiradas eliminadas: {count}")
    """
    storage = _get_storage()
    expiration_minutes = _get_expiration_minutes()
    return storage.cleanup_expired_sessions(expiration_minutes)


def get_active_sessions(username: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Obtiene lista de sesiones activas.

    Args:
        username: Si se especifica, solo sesiones de ese usuario

    Returns:
        Lista de diccionarios con datos de sesiones activas

    Example:
        >>> # Todas las sesiones
        >>> sessions = get_active_sessions()
        >>>
        >>> # Solo de un usuario
        >>> sessions = get_active_sessions('admin')
        >>> for s in sessions:
        ...     print(f"{s['username']}: {s['last_activity']}")
    """
    storage = _get_storage()
    expiration_minutes = _get_expiration_minutes()

    all_sessions = storage.get_all_sessions(username)
    active_sessions = []

    for session in all_sessions:
        last_activity = datetime.fromisoformat(session['last_activity'])
        if datetime.now() <= last_activity + timedelta(minutes=expiration_minutes):
            active_sessions.append({
                'session_id': session['session_id'],
                'username': session['username'],
                'created_at': session['created_at'],
                'last_activity': session['last_activity'],
                'expires_at': (last_activity + timedelta(minutes=expiration_minutes)).isoformat(),
                'scopes': session.get('scopes')
            })

    return active_sessions
