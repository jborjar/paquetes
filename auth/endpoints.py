"""
Funciones helper para implementar endpoints de autenticación.

Proporciona funciones para login y logout que se pueden integrar
fácilmente en Flask, FastAPI u otros frameworks.
"""
import os
from typing import Dict, Optional, Callable
from .sessions import create_session, delete_session, validate_session


def _get_user_validator() -> Optional[Callable]:
    """
    Obtiene función validadora de usuarios desde variable de entorno.

    El usuario debe proporcionar una función que valide credenciales.
    Esta función se especifica en AUTH_VALIDATOR_MODULE y AUTH_VALIDATOR_FUNCTION.

    Returns:
        Callable que recibe (username, password) y retorna True/False

    Example en .env:
        AUTH_VALIDATOR_MODULE=auth.validators
        AUTH_VALIDATOR_FUNCTION=validate_ldap_user
    """
    module_name = os.getenv('AUTH_VALIDATOR_MODULE')
    function_name = os.getenv('AUTH_VALIDATOR_FUNCTION')

    if not module_name or not function_name:
        return None

    try:
        import importlib
        module = importlib.import_module(module_name)
        validator = getattr(module, function_name)
        return validator
    except (ImportError, AttributeError) as e:
        raise ValueError(
            f"Error cargando validador de usuarios: {e}\n"
            f"Verifique AUTH_VALIDATOR_MODULE y AUTH_VALIDATOR_FUNCTION en .env"
        )


def login_user(username: str, password: str, scopes: Optional[str] = None) -> Dict:
    """
    Realiza login de usuario y crea sesión.

    Valida credenciales usando la función configurada en variables de entorno
    y crea una sesión si las credenciales son válidas.

    Args:
        username: Nombre de usuario
        password: Contraseña
        scopes: Permisos/alcances de la sesión (opcional)

    Returns:
        Dict con:
        - success: True/False
        - session: Dict con datos de sesión (si success=True)
        - error: Mensaje de error (si success=False)

    Example:
        >>> result = login_user('admin', 'password123', 'read:users,write:users')
        >>> if result['success']:
        ...     print(f"Session ID: {result['session']['session_id']}")
        >>> else:
        ...     print(f"Error: {result['error']}")

    Configuración en .env:
        AUTH_VALIDATOR_MODULE=paquetes.auth.validators
        AUTH_VALIDATOR_FUNCTION=validate_user
    """
    # Validar credenciales
    validator = _get_user_validator()

    if not validator:
        return {
            'success': False,
            'error': 'Validador de usuarios no configurado. Configure AUTH_VALIDATOR_MODULE y AUTH_VALIDATOR_FUNCTION en .env'
        }

    try:
        # Validar credenciales
        validation_result = validator(username, password)

        if not validation_result:
            return {
                'success': False,
                'error': 'Credenciales inválidas'
            }

        # Si el validador retorna un dict, extraer scopes
        # Si retorna True/bool, usar scopes del parámetro
        if isinstance(validation_result, dict):
            validated_username = validation_result.get('username', username)
            validated_scopes = validation_result.get('scopes', scopes)
        else:
            validated_username = username
            validated_scopes = scopes

        # Crear sesión
        session = create_session(validated_username, validated_scopes)

        return {
            'success': True,
            'session': session
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Error durante login: {str(e)}'
        }


def logout_user(session_id: str) -> Dict:
    """
    Realiza logout eliminando la sesión.

    Args:
        session_id: ID de la sesión a cerrar

    Returns:
        Dict con:
        - success: True/False
        - message: Mensaje descriptivo

    Example:
        >>> result = logout_user('a1b2c3d4-...')
        >>> print(result['message'])
        'Sesión cerrada exitosamente'
    """
    try:
        deleted = delete_session(session_id)

        if deleted:
            return {
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }
        else:
            return {
                'success': False,
                'message': 'Sesión no encontrada'
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'Error durante logout: {str(e)}'
        }


def get_session_info(session_id: str) -> Dict:
    """
    Obtiene información de una sesión sin renovarla.

    Args:
        session_id: ID de la sesión

    Returns:
        Dict con:
        - success: True/False
        - session: Dict con datos de sesión (si success=True)
        - error: Mensaje de error (si success=False)

    Example:
        >>> result = get_session_info('a1b2c3d4-...')
        >>> if result['success']:
        ...     print(f"Usuario: {result['session']['username']}")
        ...     print(f"Expira: {result['session']['expires_at']}")
    """
    try:
        session = validate_session(session_id, renew=False)

        if session:
            return {
                'success': True,
                'session': session
            }
        else:
            return {
                'success': False,
                'error': 'Sesión inválida o expirada'
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'Error obteniendo sesión: {str(e)}'
        }


# ============================================================================
# EJEMPLOS DE USO CON FLASK
# ============================================================================

def create_flask_auth_routes(app, prefix: str = '/api/auth'):
    """
    Crea automáticamente rutas de autenticación en una app Flask.

    Args:
        app: Instancia de Flask
        prefix: Prefijo para las rutas (default: '/api/auth')

    Example:
        >>> from flask import Flask
        >>> from paquetes.auth import create_flask_auth_routes
        >>>
        >>> app = Flask(__name__)
        >>> create_flask_auth_routes(app)
        >>>
        >>> # Ahora tiene:
        >>> # POST /api/auth/login
        >>> # POST /api/auth/logout
        >>> # GET /api/auth/session
    """
    from flask import request, jsonify

    @app.route(f'{prefix}/login', methods=['POST'])
    def login():
        """
        POST /api/auth/login - Login de usuario.

        Acepta tanto JSON como form-urlencoded.
        """
        content_type = request.headers.get('content-type', '')

        # Intentar parsear como JSON primero
        if 'application/json' in content_type:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'JSON inválido'}), 400
            username = data.get('username')
            password = data.get('password')
            scopes = data.get('scopes')

        # Si no es JSON, intentar como form-urlencoded
        elif 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
            username = request.form.get('username')
            password = request.form.get('password')
            scopes = request.form.get('scopes')

        # Si no especifica content-type, intentar JSON primero, luego form
        else:
            data = request.get_json(silent=True)
            if data:
                username = data.get('username')
                password = data.get('password')
                scopes = data.get('scopes')
            else:
                username = request.form.get('username')
                password = request.form.get('password')
                scopes = request.form.get('scopes')

        # Validar que tenemos username y password
        if not username or not password:
            return jsonify({'error': 'Falta username o password'}), 400

        result = login_user(username, password, scopes)

        if result['success']:
            return jsonify(result['session']), 200
        else:
            return jsonify({'error': result['error']}), 401

    @app.route(f'{prefix}/logout', methods=['POST'])
    def logout():
        """
        POST /api/auth/logout - Logout de usuario.

        Autenticación (elegir una opción):
        - Header: Authorization: Bearer <session_id>
        - Cookie: Sesion_Auth=<session_id>
        """
        # Obtener session_id desde header o cookie
        session_id = None
        auth_header = request.headers.get('Authorization')

        # Opción 1: Header Authorization
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                session_id = parts[1]
            else:
                return jsonify({'error': 'Formato de Authorization inválido. Use: Bearer <token>'}), 401

        # Opción 2: Cookie Sesion_Auth
        if not session_id:
            session_id = request.cookies.get('Sesion_Auth')

        if not session_id:
            return jsonify({'error': 'Falta header Authorization o cookie Sesion_Auth'}), 401

        result = logout_user(session_id)

        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['message']}), 400

    @app.route(f'{prefix}/session', methods=['GET'])
    def session():
        """
        GET /api/auth/session - Obtener info de sesión actual.

        Autenticación (elegir una opción):
        - Header: Authorization: Bearer <session_id>
        - Cookie: Sesion_Auth=<session_id>
        """
        # Obtener session_id desde header o cookie
        session_id = None
        auth_header = request.headers.get('Authorization')

        # Opción 1: Header Authorization
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                session_id = parts[1]
            else:
                return jsonify({'error': 'Formato de Authorization inválido. Use: Bearer <token>'}), 401

        # Opción 2: Cookie Sesion_Auth
        if not session_id:
            session_id = request.cookies.get('Sesion_Auth')

        if not session_id:
            return jsonify({'error': 'Falta header Authorization o cookie Sesion_Auth'}), 401

        result = get_session_info(session_id)

        if result['success']:
            return jsonify(result['session']), 200
        else:
            return jsonify({'error': result['error']}), 401


# ============================================================================
# EJEMPLOS DE USO CON FASTAPI
# ============================================================================

def create_fastapi_auth_routes(app, prefix: str = '/api/auth'):
    """
    Crea automáticamente rutas de autenticación en una app FastAPI.

    Args:
        app: Instancia de FastAPI
        prefix: Prefijo para las rutas (default: '/api/auth')

    Example:
        >>> from fastapi import FastAPI
        >>> from paquetes.auth import create_fastapi_auth_routes
        >>>
        >>> app = FastAPI()
        >>> create_fastapi_auth_routes(app)
        >>>
        >>> # Ahora tiene:
        >>> # POST /api/auth/login
        >>> # POST /api/auth/logout
        >>> # GET /api/auth/session
    """
    from fastapi import Request, HTTPException, Form, Response
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel

    class LoginRequest(BaseModel):
        username: str
        password: str
        scopes: Optional[str] = None

    @app.post(f'{prefix}/login')
    async def login(request: Request, response: Response):
        """
        POST /api/auth/login - Login de usuario.

        Acepta tanto JSON como form-urlencoded.
        """
        content_type = request.headers.get('content-type', '')

        # Intentar parsear como JSON primero
        if 'application/json' in content_type:
            try:
                data = await request.json()
                username = data.get('username')
                password = data.get('password')
                scopes = data.get('scopes')
            except Exception:
                raise HTTPException(status_code=400, detail='JSON inválido')

        # Si no es JSON, intentar como form-urlencoded
        elif 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
            try:
                form_data = await request.form()
                username = form_data.get('username')
                password = form_data.get('password')
                scopes = form_data.get('scopes')
            except Exception:
                raise HTTPException(status_code=400, detail='Form data inválido')

        # Si no especifica content-type, intentar JSON primero, luego form
        else:
            try:
                data = await request.json()
                username = data.get('username')
                password = data.get('password')
                scopes = data.get('scopes')
            except Exception:
                try:
                    form_data = await request.form()
                    username = form_data.get('username')
                    password = form_data.get('password')
                    scopes = form_data.get('scopes')
                except Exception:
                    raise HTTPException(status_code=400, detail='Formato de datos no soportado. Use JSON o form-urlencoded')

        # Validar que tenemos username y password
        if not username or not password:
            raise HTTPException(status_code=400, detail='Falta username o password')

        result = login_user(username, password, scopes)

        if result['success']:
            # Setear cookie con el session_id
            session_data = result['session']
            json_response = JSONResponse(content=session_data)
            json_response.set_cookie(
                key='Sesion_Auth',
                value=session_data['session_id'],
                path='/',
                httponly=True,
                samesite='lax',
                secure=False  # Cambiar a True en producción con HTTPS
            )
            return json_response
        else:
            raise HTTPException(status_code=401, detail=result['error'])

    @app.post(f'{prefix}/logout')
    async def logout(request: Request):
        """
        POST /api/auth/logout - Logout de usuario.

        Autenticación (elegir una opción):
        - Header: Authorization: Bearer <session_id>
        - Cookie: Sesion_Auth=<session_id>
        """
        # Obtener session_id desde header o cookie
        session_id = None
        auth_header = request.headers.get('Authorization')

        # Opción 1: Header Authorization
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                session_id = parts[1]
            else:
                raise HTTPException(
                    status_code=401,
                    detail='Formato de Authorization inválido. Use: Bearer <token>'
                )

        # Opción 2: Cookie Sesion_Auth
        if not session_id:
            session_id = request.cookies.get('Sesion_Auth')

        if not session_id:
            raise HTTPException(
                status_code=401,
                detail='Falta header Authorization o cookie Sesion_Auth'
            )

        result = logout_user(session_id)

        if result['success']:
            # Eliminar la cookie
            json_response = JSONResponse(content={'message': result['message']})
            json_response.delete_cookie(key='Sesion_Auth')
            return json_response
        else:
            raise HTTPException(status_code=400, detail=result['message'])

    @app.get(f'{prefix}/session')
    async def session(request: Request):
        """
        GET /api/auth/session - Obtener info de sesión actual.

        Autenticación (elegir una opción):
        - Header: Authorization: Bearer <session_id>
        - Cookie: Sesion_Auth=<session_id>
        """
        # Obtener session_id desde header o cookie
        session_id = None
        auth_header = request.headers.get('Authorization')

        # Opción 1: Header Authorization
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                session_id = parts[1]
            else:
                raise HTTPException(
                    status_code=401,
                    detail='Formato de Authorization inválido. Use: Bearer <token>'
                )

        # Opción 2: Cookie Sesion_Auth
        if not session_id:
            session_id = request.cookies.get('Sesion_Auth')

        if not session_id:
            raise HTTPException(
                status_code=401,
                detail='Falta header Authorization o cookie Sesion_Auth'
            )

        result = get_session_info(session_id)

        if result['success']:
            return result['session']
        else:
            raise HTTPException(status_code=401, detail=result['error'])
