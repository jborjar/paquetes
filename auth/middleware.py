"""
Middleware y decoradores para proteger endpoints.

Proporciona decoradores para validar sesiones en rutas protegidas.
"""
from functools import wraps
from typing import Callable, Optional

try:
    from fastapi import Request
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False
    Request = None

from .sessions import validate_session


def require_auth(scopes: Optional[str] = None):
    """
    Decorador para proteger endpoints que requieren autenticación.

    Valida el SessionID del header 'Authorization' y renueva la sesión
    automáticamente (sliding expiration).

    Args:
        scopes: Permisos requeridos (opcional). Si se especifica, valida
                que la sesión tenga los scopes necesarios.

    Returns:
        Decorador que valida la sesión

    Example con Flask:
        >>> from flask import Flask, request, jsonify
        >>> from paquetes.auth import require_auth
        >>>
        >>> app = Flask(__name__)
        >>>
        >>> @app.route('/api/protected')
        >>> @require_auth()
        >>> def protected_route(session):
        ...     return jsonify({
        ...         'message': 'Acceso permitido',
        ...         'user': session['username']
        ...     })
        >>>
        >>> @app.route('/api/admin')
        >>> @require_auth(scopes='admin')
        >>> def admin_route(session):
        ...     return jsonify({'message': 'Admin access'})

    Example con FastAPI:
        >>> from fastapi import FastAPI, Request, HTTPException
        >>> from paquetes.auth import require_auth
        >>>
        >>> app = FastAPI()
        >>>
        >>> @app.get('/api/protected')
        >>> @require_auth()
        >>> async def protected_route(request: Request, session: dict):
        ...     return {
        ...         'message': 'Acceso permitido',
        ...         'user': session['username']
        ...     }

    Header esperado:
        Authorization: Bearer <session_id>

    O Cookie:
        Sesion_Auth=<session_id>
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Intentar obtener el request de args o kwargs
            request = None

            # Flask: primer argumento puede ser request si se usa @app.route
            # FastAPI: request puede estar en kwargs
            if args and hasattr(args[0], 'headers'):
                request = args[0]
            elif 'request' in kwargs:
                request = kwargs['request']

            # Obtener token del header Authorization o cookie Sesion_Auth
            session_id = None
            auth_header = None

            if request and hasattr(request, 'headers'):
                auth_header = request.headers.get('Authorization')

            # Opción 1: Desde header Authorization
            if auth_header:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    session_id = parts[1]
                else:
                    # Formato inválido del header
                    if hasattr(request, 'json'):  # Flask-like
                        from flask import jsonify
                        return jsonify({'error': 'Formato de Authorization inválido. Use: Bearer <token>'}), 401
                    else:  # FastAPI-like
                        from fastapi import HTTPException
                        raise HTTPException(
                            status_code=401,
                            detail='Formato de Authorization inválido. Use: Bearer <token>'
                        )

            # Opción 2: Desde cookie Sesion_Auth
            if not session_id and request and hasattr(request, 'cookies'):
                session_id = request.cookies.get('Sesion_Auth')

            # Si no hay token en ninguna parte, retornar error
            if not session_id:
                if hasattr(request, 'json'):  # Flask-like
                    from flask import jsonify
                    return jsonify({'error': 'Autorización requerida'}), 401
                else:  # FastAPI-like
                    from fastapi import HTTPException
                    raise HTTPException(status_code=401, detail='Autorización requerida')

            # Validar sesión (con renovación automática)
            session = validate_session(session_id, renew=True)

            if not session:
                if hasattr(request, 'json'):  # Flask-like
                    from flask import jsonify
                    return jsonify({'error': 'Autorización requerida'}), 401
                else:  # FastAPI-like
                    from fastapi import HTTPException
                    raise HTTPException(status_code=401, detail='Autorización requerida')

            # Validar scopes si se especificaron
            if scopes:
                import re
                session_scopes = session.get('scopes', '')
                required_scopes = [s.strip() for s in scopes.split(',')]
                user_scopes = [s.strip() for s in session_scopes.split(',')] if session_scopes else []

                # Verificar cada scope requerido
                for required in required_scopes:
                    matched = False

                    # Parsear scope requerido: subsistema:permisos
                    if ':' in required:
                        req_subsystem, req_perms = required.split(':', 1)
                        req_perms_list = [p.strip() for p in req_perms.split(',')]

                        # Verificar contra cada scope del usuario
                        for user_scope in user_scopes:
                            if ':' not in user_scope:
                                continue

                            user_subsystem, user_perms = user_scope.split(':', 1)
                            user_perms_list = [p.strip() for p in user_perms.split(',')]

                            # Verificar subsistema (con wildcard)
                            subsystem_match = False
                            if '*' in req_subsystem:
                                pattern = req_subsystem.replace('*', '.*')
                                pattern = f'^{pattern}$'
                                if re.match(pattern, user_subsystem):
                                    subsystem_match = True
                            else:
                                if req_subsystem == user_subsystem:
                                    subsystem_match = True

                            # Si el subsistema coincide, verificar permisos
                            if subsystem_match:
                                # El usuario debe tener TODOS los permisos requeridos
                                # O tener 'admin' que incluye todos los permisos
                                if 'admin' in user_perms_list:
                                    matched = True
                                    break
                                elif all(perm in user_perms_list for perm in req_perms_list):
                                    matched = True
                                    break
                    else:
                        # Comparación exacta (sin formato subsistema:permisos)
                        if required in user_scopes:
                            matched = True

                    if not matched:
                        if hasattr(request, 'json'):  # Flask-like
                            from flask import jsonify
                            return jsonify({'error': 'Permisos insuficientes'}), 403
                        else:  # FastAPI-like
                            from fastapi import HTTPException
                            raise HTTPException(status_code=403, detail='Permisos insuficientes')

            # Inyectar sesión en kwargs
            kwargs['session'] = session

            # Llamar función original
            return func(*args, **kwargs)

        return wrapper
    return decorator


def get_session_from_request(request) -> Optional[dict]:
    """
    Extrae y valida sesión desde un request sin usar decorador.

    Útil para casos donde se necesita validación manual.

    Busca el token en:
    1. Header Authorization: Bearer <token>
    2. Cookie Sesion_Auth

    Args:
        request: Objeto request (Flask o FastAPI)

    Returns:
        Dict con datos de sesión si es válida, None si no

    Example:
        >>> from flask import request
        >>> from paquetes.auth import get_session_from_request
        >>>
        >>> @app.route('/api/optional-auth')
        >>> def optional_auth():
        ...     session = get_session_from_request(request)
        ...     if session:
        ...         return f"Hola {session['username']}"
        ...     else:
        ...         return "Hola invitado"
    """
    if not hasattr(request, 'headers'):
        return None

    session_id = None

    # Opción 1: Desde header Authorization
    auth_header = request.headers.get('Authorization')
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            session_id = parts[1]

    # Opción 2: Desde cookie Sesion_Auth
    if not session_id and hasattr(request, 'cookies'):
        session_id = request.cookies.get('Sesion_Auth')

    if not session_id:
        return None

    return validate_session(session_id, renew=True)


#============================================================================
# FAST API DEPENDENCIES
# ============================================================================

class SessionDependency:
    """
    Dependencia de FastAPI para obtener la sesión actual.

    Clase callable que FastAPI puede usar con Depends() sin exponer
    el parámetro Request en el schema de OpenAPI.
    """
    def __init__(self, scopes: Optional[str] = None):
        """
        Args:
            scopes: Scopes requeridos (opcional). Si se especifica, valida
                    que la sesión tenga los scopes necesarios.
        """
        self.scopes = scopes

    def __call__(self, request: Request):
        """
        Método callable que FastAPI ejecutará automáticamente.

        FastAPI inyecta el Request automáticamente sin exponerlo en la API.
        """
        # Obtener token del header Authorization o cookie Sesion_Auth
        session_id = None
        auth_header = None

        if hasattr(request, 'headers'):
            auth_header = request.headers.get('Authorization')

        # Opción 1: Desde header Authorization
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                session_id = parts[1]
            else:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=401,
                    detail='Formato de Authorization inválido. Use: Bearer <token>'
                )

        # Opción 2: Desde cookie Sesion_Auth
        if not session_id and hasattr(request, 'cookies'):
            session_id = request.cookies.get('Sesion_Auth')

        if not session_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail='Autorización requerida')

        # Validar sesión (con renovación automática)
        session = validate_session(session_id, renew=True)

        if not session:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail='Autorización requerida')

        # Validar scopes si se especificaron
        if self.scopes:
            session_scopes = session.get('scopes', '')
            required_scopes = [s.strip() for s in self.scopes.split(',')]
            user_scopes = [s.strip() for s in session_scopes.split(',')] if session_scopes else []

            # Verificar cada scope requerido
            for required in required_scopes:
                matched = False

                # Parsear scope requerido: subsistema:permisos
                if ':' in required:
                    import re
                    req_subsystem, req_perms = required.split(':', 1)
                    req_perms_list = [p.strip() for p in req_perms.split(',')]

                    # Verificar contra cada scope del usuario
                    for user_scope in user_scopes:
                        if ':' not in user_scope:
                            continue

                        user_subsystem, user_perms = user_scope.split(':', 1)
                        user_perms_list = [p.strip() for p in user_perms.split(',')]

                        # Verificar subsistema (con wildcard)
                        subsystem_match = False
                        if '*' in req_subsystem:
                            pattern = req_subsystem.replace('*', '.*')
                            pattern = f'^{pattern}$'
                            if re.match(pattern, user_subsystem):
                                subsystem_match = True
                        else:
                            if req_subsystem == user_subsystem:
                                subsystem_match = True

                        # Si el subsistema coincide, verificar permisos
                        if subsystem_match:
                            # El usuario debe tener TODOS los permisos requeridos
                            # O tener 'admin' que incluye todos los permisos
                            if 'admin' in user_perms_list:
                                matched = True
                                break
                            elif all(perm in user_perms_list for perm in req_perms_list):
                                matched = True
                                break
                else:
                    # Comparación exacta (sin formato subsistema:permisos)
                    if required in user_scopes:
                        matched = True

                if not matched:
                    from fastapi import HTTPException
                    raise HTTPException(status_code=403, detail='Permisos insuficientes')

        return session


def get_current_session(scopes: Optional[str] = None):
    """
    Factory para crear una dependencia de sesión de FastAPI.

    Usa el sistema Depends() de FastAPI para inyectar la sesión sin que
    FastAPI lo interprete como un parámetro del request body.

    Args:
        scopes: Scopes requeridos (opcional). Si se especifica, valida
                que la sesión tenga los scopes necesarios.

    Returns:
        Instancia de SessionDependency que FastAPI puede usar con Depends()

    Example:
        >>> from fastapi import FastAPI, Depends
        >>> from paquetes.auth import get_current_session
        >>>
        >>> app = FastAPI()
        >>>
        >>> @app.get('/api/admin')
        >>> async def admin_route(
        ...     session: dict = Depends(get_current_session(scopes='admin'))
        ... ):
        ...     return {'message': 'Admin access', 'user': session['username']}
    """
    return SessionDependency(scopes=scopes)
