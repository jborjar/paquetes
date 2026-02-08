"""
Ejemplo completo de autenticación con FastAPI.

Este script muestra cómo integrar el sistema de autenticación
en una aplicación FastAPI con configuración flexible de endpoints y base de datos.

Características:
- Endpoint base configurable (/, /auth, /api/auth, etc.)
- Base de datos configurable (por parámetro o variable de entorno)
- Rutas de autenticación completas
- Ejemplos de rutas protegidas con scopes
- Documentación automática con Swagger UI

Uso:
    1. Configurar .env con credenciales MSSQL
    2. Crear validador de usuarios (ver example_validators.py)
    3. Ejecutar con configuración por defecto:
       python paquetes/tests/example_auth_fastapi.py

    4. O personalizar en tu aplicación:
       from auth_fastapi import create_auth_app  # Importar desde raíz de app
       app = create_auth_app(endpoint_prefix='/auth', database='mi_db')
       uvicorn.run(app, host='0.0.0.0', port=8000)

    NOTA: auth_fastapi.py está en la raíz de la aplicación (/app/), no en paquetes/
"""
import os
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from paquetes.auth import (
    ensure_sessions_table,
    require_auth,
    login_user,
    logout_user,
    get_active_sessions,
    cleanup_expired_sessions,
    get_session_from_request
)


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class LoginRequest(BaseModel):
    """Modelo para petición de login."""
    username: str
    password: str
    scopes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "password123",
                "scopes": "read:users,write:users,admin"
            }
        }


class LoginResponse(BaseModel):
    """Modelo para respuesta de login."""
    session_id: str
    username: str
    created_at: str
    expires_at: str
    scopes: Optional[str] = None


class MessageResponse(BaseModel):
    """Modelo para respuesta con mensaje."""
    message: str


class ErrorResponse(BaseModel):
    """Modelo para respuesta de error."""
    error: str


# ============================================================================
# FUNCIÓN PRINCIPAL PARA CREAR APP
# ============================================================================

def create_auth_app(
    endpoint_prefix: str = '/api/auth',
    database: str = None,
    public_prefix: str = '/api',
    title: str = "Auth API",
    version: str = "1.0.0"
):
    """
    Crea una aplicación FastAPI con autenticación configurada.

    Args:
        endpoint_prefix: Prefijo para endpoints de autenticación (default: '/api/auth')
                        Ejemplos: '/', '/auth', '/api/auth', '/v1/auth'
        database: Nombre de la base de datos MSSQL (default: usa MSSQL_DATABASE del .env)
        public_prefix: Prefijo para rutas públicas y protegidas (default: '/api')
        title: Título de la API para documentación (default: 'Auth API')
        version: Versión de la API (default: '1.0.0')

    Returns:
        FastAPI: Aplicación FastAPI configurada

    Example:
        >>> # Con endpoints en /auth/login, /auth/logout
        >>> app = create_auth_app(endpoint_prefix='/auth')
        >>>
        >>> # Con endpoints en /login, /logout (raíz)
        >>> app = create_auth_app(endpoint_prefix='')
        >>>
        >>> # Con base de datos específica
        >>> app = create_auth_app(database='mi_database')
    """
    # Configurar base de datos si se especificó
    if database:
        os.environ['MSSQL_DATABASE'] = database

    # Normalizar prefijos (eliminar / al final)
    endpoint_prefix = endpoint_prefix.rstrip('/')
    public_prefix = public_prefix.rstrip('/')

    # Crear app FastAPI
    app = FastAPI(
        title=title,
        description="Sistema de autenticación con session tokens y sliding expiration",
        version=version
    )

    # ========================================================================
    # EVENTOS DE INICIO
    # ========================================================================

    @app.on_event("startup")
    async def startup_event():
        """Inicializar tabla de sesiones al arrancar."""
        print(f"Inicializando tabla USER_SESSIONS en base de datos: {os.getenv('MSSQL_DATABASE', 'default')}...")
        ensure_sessions_table()
        print("✓ Tabla lista")

    # ========================================================================
    # RUTAS DE AUTENTICACIÓN
    # ========================================================================

    @app.post(
        f"{endpoint_prefix}/login",
        response_model=LoginResponse,
        responses={
            200: {"description": "Login exitoso"},
            400: {"description": "Faltan campos requeridos"},
            401: {"description": "Credenciales inválidas"}
        },
        tags=["Autenticación"]
    )
    async def login(data: LoginRequest):
        """
        Login de usuario.

        Crea una nueva sesión si las credenciales son válidas.
        Retorna el session_id que debe usarse en el header Authorization.

        Ejemplo de uso:
        ```bash
        curl -X POST http://localhost:8000{endpoint_prefix}/login \\
          -H "Content-Type: application/json" \\
          -d '{"username": "admin", "password": "password123"}'
        ```
        """
        result = login_user(data.username, data.password, data.scopes)

        if result['success']:
            return result['session']
        else:
            raise HTTPException(status_code=401, detail=result['error'])

    @app.post(
        f"{endpoint_prefix}/logout",
        response_model=MessageResponse,
        responses={
            200: {"description": "Logout exitoso"},
            401: {"description": "Falta header Authorization o formato inválido"},
            400: {"description": "Error durante logout"}
        },
        tags=["Autenticación"]
    )
    async def logout(request: Request):
        """
        Logout de usuario.

        Elimina la sesión actual.

        Header requerido:
        - Authorization: Bearer <session_id>

        Ejemplo de uso:
        ```bash
        curl -X POST http://localhost:8000{endpoint_prefix}/logout \\
          -H "Authorization: Bearer a1b2c3d4-..."
        ```
        """
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            raise HTTPException(status_code=401, detail='Falta header Authorization')

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise HTTPException(
                status_code=401,
                detail='Formato de Authorization inválido. Use: Bearer <token>'
            )

        session_id = parts[1]
        result = logout_user(session_id)

        if result['success']:
            return {"message": result['message']}
        else:
            raise HTTPException(status_code=400, detail=result['message'])

    @app.get(
        f"{endpoint_prefix}/session",
        responses={
            200: {"description": "Información de sesión"},
            401: {"description": "Sesión inválida o expirada"}
        },
        tags=["Autenticación"]
    )
    async def session_info(request: Request):
        """
        Obtener información de sesión actual.

        No renueva la sesión, solo retorna información.

        Header requerido:
        - Authorization: Bearer <session_id>

        Ejemplo de uso:
        ```bash
        curl http://localhost:8000{endpoint_prefix}/session \\
          -H "Authorization: Bearer a1b2c3d4-..."
        ```
        """
        session = get_session_from_request(request)

        if session:
            return session
        else:
            raise HTTPException(status_code=401, detail='Sesión inválida o expirada')

    # ========================================================================
    # RUTAS PÚBLICAS Y PROTEGIDAS
    # ========================================================================

    @app.get(
        f"{public_prefix}/public",
        tags=["Público"]
    )
    async def public_route():
        """
        Ruta pública - No requiere autenticación.

        Ejemplo de uso:
        ```bash
        curl http://localhost:8000{public_prefix}/public
        ```
        """
        return {
            'message': 'Esta ruta es pública',
            'timestamp': datetime.now().isoformat()
        }

    @app.get(
        f"{public_prefix}/protected",
        responses={
            200: {"description": "Acceso permitido"},
            401: {"description": "No autenticado"}
        },
        tags=["Protegido"]
    )
    @require_auth()
    async def protected_route(request: Request, session: dict):
        """
        Ruta protegida - Requiere autenticación.

        Header requerido:
        - Authorization: Bearer <session_id>

        La sesión se renueva automáticamente (sliding expiration).

        Ejemplo de uso:
        ```bash
        curl http://localhost:8000{public_prefix}/protected \\
          -H "Authorization: Bearer a1b2c3d4-..."
        ```
        """
        return {
            'message': 'Acceso permitido',
            'user': session['username'],
            'scopes': session.get('scopes'),
            'expires_at': session['expires_at']
        }

    @app.get(
        f"{public_prefix}/admin",
        responses={
            200: {"description": "Acceso admin permitido"},
            401: {"description": "No autenticado"},
            403: {"description": "Permisos insuficientes"}
        },
        tags=["Admin"]
    )
    @require_auth(scopes='admin')
    async def admin_route(request: Request, session: dict):
        """
        Ruta admin - Requiere scope 'admin'.

        Header requerido:
        - Authorization: Bearer <session_id>

        El usuario debe tener el scope 'admin' en su sesión.

        Ejemplo de uso:
        ```bash
        curl http://localhost:8000{public_prefix}/admin \\
          -H "Authorization: Bearer a1b2c3d4-..."
        ```
        """
        return {
            'message': 'Admin access granted',
            'user': session['username']
        }

    @app.get(
        f"{public_prefix}/sessions",
        responses={
            200: {"description": "Lista de sesiones activas"},
            401: {"description": "No autenticado"},
            403: {"description": "Permisos insuficientes"}
        },
        tags=["Admin"]
    )
    @require_auth(scopes='admin')
    async def list_sessions(
        request: Request,
        session: dict,
        username: Optional[str] = Query(None, description="Filtrar por usuario")
    ):
        """
        Lista sesiones activas - Requiere scope 'admin'.

        Query params:
        - username: Filtrar por usuario (opcional)

        Header requerido:
        - Authorization: Bearer <session_id>

        Ejemplo de uso:
        ```bash
        # Todas las sesiones
        curl http://localhost:8000{public_prefix}/sessions \\
          -H "Authorization: Bearer a1b2c3d4-..."

        # Sesiones de un usuario específico
        curl "http://localhost:8000{public_prefix}/sessions?username=admin" \\
          -H "Authorization: Bearer a1b2c3d4-..."
        ```
        """
        sessions = get_active_sessions(username)

        return {
            'sessions': sessions,
            'total': len(sessions)
        }

    # ========================================================================
    # UTILIDADES
    # ========================================================================

    @app.post(
        f"{public_prefix}/cleanup",
        response_model=dict,
        responses={
            200: {"description": "Sesiones expiradas eliminadas"},
            401: {"description": "No autenticado"},
            403: {"description": "Permisos insuficientes"}
        },
        tags=["Admin"]
    )
    @require_auth(scopes='admin')
    async def cleanup(request: Request, session: dict):
        """
        Eliminar sesiones expiradas - Requiere scope 'admin'.

        Header requerido:
        - Authorization: Bearer <session_id>

        Ejemplo de uso:
        ```bash
        curl -X POST http://localhost:8000{public_prefix}/cleanup \\
          -H "Authorization: Bearer a1b2c3d4-..."
        ```
        """
        count = cleanup_expired_sessions()
        return {
            'message': 'Sesiones expiradas eliminadas',
            'count': count
        }

    @app.get(
        f"{public_prefix}/health",
        tags=["Utilidades"]
    )
    async def health():
        """
        Health check - Verificar estado del servicio.

        Ejemplo de uso:
        ```bash
        curl http://localhost:8000{public_prefix}/health
        ```
        """
        return {
            'status': 'ok',
            'service': 'Auth API',
            'database': os.getenv('MSSQL_DATABASE', 'default'),
            'endpoint_prefix': endpoint_prefix,
            'public_prefix': public_prefix,
            'timestamp': datetime.now().isoformat()
        }

    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """Handler para rutas no encontradas."""
        return JSONResponse(
            status_code=404,
            content={'error': 'Endpoint no encontrado'}
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        """Handler para errores internos."""
        return JSONResponse(
            status_code=500,
            content={'error': 'Error interno del servidor'}
        )

    return app


# ============================================================================
# MAIN - CONFIGURACIÓN POR DEFECTO
# ============================================================================

if __name__ == '__main__':
    import uvicorn

    print("=" * 80)
    print("API de Autenticación (FastAPI)")
    print("=" * 80)
    print()
    print("Configuración:")
    print(f"  Base de datos: {os.getenv('MSSQL_DATABASE', 'default')}")
    print(f"  Endpoint auth: /api/auth")
    print(f"  Endpoint público: /api")
    print()
    print("Endpoints disponibles:")
    print()
    print("Autenticación:")
    print("  POST   /api/auth/login         - Login de usuario")
    print("  POST   /api/auth/logout        - Logout de usuario")
    print("  GET    /api/auth/session       - Info de sesión actual")
    print()
    print("Rutas de ejemplo:")
    print("  GET    /api/public             - Ruta pública")
    print("  GET    /api/protected          - Ruta protegida")
    print("  GET    /api/admin              - Ruta admin")
    print("  GET    /api/sessions           - Lista sesiones activas (admin)")
    print()
    print("Utilidades:")
    print("  POST   /api/cleanup            - Eliminar sesiones expiradas (admin)")
    print("  GET    /api/health             - Health check")
    print()
    print("=" * 80)
    print()
    print("Para personalizar, importa create_auth_app():")
    print("  from auth_fastapi import create_auth_app  # Desde raíz de app")
    print("  app = create_auth_app(endpoint_prefix='/auth', database='mi_db')")
    print()
    print("Iniciando servidor en http://localhost:8000")
    print("Documentación interactiva: http://localhost:8000/docs")
    print("Documentación alternativa: http://localhost:8000/redoc")
    print()

    # Crear app con configuración por defecto
    app = create_auth_app()

    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_level='info'
    )
