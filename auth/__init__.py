"""
Paquete de autenticación con session tokens y sliding expiration.

Portable y genérico - soporta múltiples backends de almacenamiento:
- JSON (por defecto, sin dependencias)
- MSSQL (requiere configuración)
- Otros backends personalizados

Proporciona:
- Gestión de sesiones con múltiples backends
- Sliding expiration (renovación automática)
- Decoradores para proteger rutas
- Helpers para endpoints de login/logout
- Soporte para Flask y FastAPI

Configuración del backend:
    from paquetes.auth import configure_storage
    from paquetes.auth.storage_json import JSONSessionStorage

    # Usar JSON (por defecto)
    configure_storage(JSONSessionStorage('sessions.json'))

    # Usar MSSQL
    from paquetes.auth.storage_mssql import MSSQLSessionStorage
    from paquetes.mssql import get_mssql_connection
    configure_storage(MSSQLSessionStorage(get_mssql_connection))
"""

# Gestión de sesiones
from .sessions import (
    create_session,
    validate_session,
    delete_session,
    delete_user_sessions,
    cleanup_expired_sessions,
    get_active_sessions,
    configure_storage,
    ensure_sessions_table
)

# Middleware y decoradores
from .middleware import (
    require_auth,
    get_session_from_request,
    get_current_session
)

# Endpoints helpers
from .endpoints import (
    login_user,
    logout_user,
    get_session_info,
    create_flask_auth_routes,
    create_fastapi_auth_routes
)

__all__ = [
    # === Configuración ===
    'configure_storage',
    'ensure_sessions_table',

    # === Gestión de Sesiones ===
    'create_session',
    'validate_session',
    'delete_session',
    'delete_user_sessions',
    'cleanup_expired_sessions',
    'get_active_sessions',

    # === Middleware ===
    'require_auth',
    'get_session_from_request',
    'get_current_session',

    # === Endpoints Helpers ===
    'login_user',
    'logout_user',
    'get_session_info',
    'create_flask_auth_routes',
    'create_fastapi_auth_routes',
]
