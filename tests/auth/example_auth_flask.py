"""
Ejemplo completo de autenticación con Flask.

Este script muestra cómo integrar el sistema de autenticación
en una aplicación Flask con configuración flexible de endpoints y base de datos.

Características:
- Endpoint base configurable (/, /auth, /api/auth, etc.)
- Base de datos configurable (por parámetro o variable de entorno)
- Rutas de autenticación completas
- Ejemplos de rutas protegidas con scopes

Uso:
    1. Configurar .env con credenciales MSSQL
    2. Crear validador de usuarios (ver example_validators.py)
    3. Ejecutar con configuración por defecto:
       python paquetes/tests/example_auth_flask.py

    4. O personalizar en tu aplicación:
       from paquetes.auth_flask import create_auth_app
       app = create_auth_app(endpoint_prefix='/auth', database='mi_db')
       app.run()
"""
import os
from flask import Flask, request, jsonify
from paquetes.auth import (
    ensure_sessions_table,
    require_auth,
    login_user,
    logout_user,
    get_active_sessions,
    cleanup_expired_sessions,
    get_session_from_request
)


def create_auth_app(
    endpoint_prefix: str = '/api/auth',
    database: str = None,
    public_prefix: str = '/api'
):
    """
    Crea una aplicación Flask con autenticación configurada.

    Args:
        endpoint_prefix: Prefijo para endpoints de autenticación (default: '/api/auth')
                        Ejemplos: '/', '/auth', '/api/auth', '/v1/auth'
        database: Nombre de la base de datos MSSQL (default: usa MSSQL_DATABASE del .env)
        public_prefix: Prefijo para rutas públicas y protegidas (default: '/api')

    Returns:
        Flask: Aplicación Flask configurada

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
    # Crear app Flask
    app = Flask(__name__)

    # Configurar base de datos si se especificó
    if database:
        os.environ['MSSQL_DATABASE'] = database

    # Normalizar prefijos (eliminar / al final)
    endpoint_prefix = endpoint_prefix.rstrip('/')
    public_prefix = public_prefix.rstrip('/')

    # ========================================================================
    # INICIALIZACIÓN
    # ========================================================================

    @app.before_first_request
    def initialize():
        """Inicializar tabla de sesiones."""
        print(f"Inicializando tabla USER_SESSIONS en base de datos: {os.getenv('MSSQL_DATABASE', 'default')}...")
        ensure_sessions_table()
        print("✓ Tabla lista")

    # ========================================================================
    # RUTAS DE AUTENTICACIÓN
    # ========================================================================

    @app.route(f'{endpoint_prefix}/login', methods=['POST'])
    def login():
        """
        POST {endpoint_prefix}/login - Login de usuario.

        Body:
        {
            "username": "admin",
            "password": "password123",
            "scopes": "read:users,write:users,admin"  // opcional
        }

        Response 200:
        {
            "session_id": "a1b2c3d4-...",
            "username": "admin",
            "created_at": "2026-01-24T08:00:00",
            "expires_at": "2026-01-24T08:30:00",
            "scopes": "read:users,write:users,admin"
        }

        Response 401:
        {
            "error": "Credenciales inválidas"
        }
        """
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Falta username o password'}), 400

        username = data['username']
        password = data['password']
        scopes = data.get('scopes')

        result = login_user(username, password, scopes)

        if result['success']:
            return jsonify(result['session']), 200
        else:
            return jsonify({'error': result['error']}), 401

    @app.route(f'{endpoint_prefix}/logout', methods=['POST'])
    def logout():
        """
        POST {endpoint_prefix}/logout - Logout de usuario.

        Headers:
            Authorization: Bearer <session_id>

        Response 200:
        {
            "message": "Sesión cerrada exitosamente"
        }

        Response 401:
        {
            "error": "Falta header Authorization"
        }
        """
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Falta header Authorization'}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de Authorization inválido. Use: Bearer <token>'}), 401

        session_id = parts[1]
        result = logout_user(session_id)

        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['message']}), 400

    @app.route(f'{endpoint_prefix}/session', methods=['GET'])
    def session_info():
        """
        GET {endpoint_prefix}/session - Obtener info de sesión actual.

        Headers:
            Authorization: Bearer <session_id>

        Response 200:
        {
            "session_id": "a1b2c3d4-...",
            "username": "admin",
            "created_at": "2026-01-24T08:00:00",
            "last_activity": "2026-01-24T08:15:00",
            "expires_at": "2026-01-24T08:45:00",
            "scopes": "read:users,write:users,admin"
        }
        """
        session = get_session_from_request(request)

        if session:
            return jsonify(session), 200
        else:
            return jsonify({'error': 'Sesión inválida o expirada'}), 401

    # ========================================================================
    # RUTAS PÚBLICAS Y PROTEGIDAS
    # ========================================================================

    @app.route(f'{public_prefix}/public', methods=['GET'])
    def public_route():
        """
        GET {public_prefix}/public - Ruta pública (sin autenticación).

        Response 200:
        {
            "message": "Esta ruta es pública",
            "timestamp": "2026-01-24T08:00:00"
        }
        """
        from datetime import datetime
        return jsonify({
            'message': 'Esta ruta es pública',
            'timestamp': datetime.now().isoformat()
        })

    @app.route(f'{public_prefix}/protected', methods=['GET'])
    @require_auth()
    def protected_route(session):
        """
        GET {public_prefix}/protected - Ruta protegida (requiere autenticación).

        Headers:
            Authorization: Bearer <session_id>

        Response 200:
        {
            "message": "Acceso permitido",
            "user": "admin",
            "scopes": "read:users,write:users,admin"
        }

        Response 401:
        {
            "error": "Sesión inválida o expirada"
        }
        """
        return jsonify({
            'message': 'Acceso permitido',
            'user': session['username'],
            'scopes': session.get('scopes')
        })

    @app.route(f'{public_prefix}/admin', methods=['GET'])
    @require_auth(scopes='admin')
    def admin_route(session):
        """
        GET {public_prefix}/admin - Ruta admin (requiere scope 'admin').

        Headers:
            Authorization: Bearer <session_id>

        Response 200:
        {
            "message": "Admin access granted",
            "user": "admin"
        }

        Response 403:
        {
            "error": "Permisos insuficientes"
        }
        """
        return jsonify({
            'message': 'Admin access granted',
            'user': session['username']
        })

    @app.route(f'{public_prefix}/sessions', methods=['GET'])
    @require_auth(scopes='admin')
    def list_sessions(session):
        """
        GET {public_prefix}/sessions - Lista sesiones activas (requiere admin).

        Query params:
            username: Filtrar por usuario (opcional)

        Headers:
            Authorization: Bearer <session_id>

        Response 200:
        {
            "sessions": [...],
            "total": 1
        }
        """
        username = request.args.get('username')
        sessions = get_active_sessions(username)

        return jsonify({
            'sessions': sessions,
            'total': len(sessions)
        })

    # ========================================================================
    # UTILIDADES
    # ========================================================================

    @app.route(f'{public_prefix}/cleanup', methods=['POST'])
    @require_auth(scopes='admin')
    def cleanup(session):
        """
        POST {public_prefix}/cleanup - Eliminar sesiones expiradas (requiere admin).

        Headers:
            Authorization: Bearer <session_id>

        Response 200:
        {
            "message": "Sesiones expiradas eliminadas",
            "count": 5
        }
        """
        count = cleanup_expired_sessions()
        return jsonify({
            'message': 'Sesiones expiradas eliminadas',
            'count': count
        })

    @app.route(f'{public_prefix}/health', methods=['GET'])
    def health():
        """GET {public_prefix}/health - Health check."""
        return jsonify({
            'status': 'ok',
            'service': 'Auth API',
            'database': os.getenv('MSSQL_DATABASE', 'default'),
            'endpoint_prefix': endpoint_prefix,
            'public_prefix': public_prefix
        })

    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint no encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500

    return app


# ============================================================================
# MAIN - CONFIGURACIÓN POR DEFECTO
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("API de Autenticación (Flask)")
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
    print("  from paquetes.auth_flask import create_auth_app")
    print("  app = create_auth_app(endpoint_prefix='/auth', database='mi_db')")
    print()
    print("Iniciando servidor en http://localhost:5000")
    print()

    # Crear app con configuración por defecto
    app = create_auth_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
